def get_values(*names):
    import json
    _all_values = json.loads("""{"pipette_type":"p50_multi","pipette_mount":"right","sample_number":8,"sample_volume":25,"bead_ratio":0.85,"elution_buffer_volume":200,"incubation_time":4,"settling_time":5,"drying_time":7}""")
    return [_all_values[n] for n in names]


import math

metadata = {
    'protocolName': 'DNA Purification',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.0'
    }


def run(protocol_context):

    [pipette_type, pipette_mount, sample_number, sample_volume, bead_ratio,
     elution_buffer_volume, incubation_time, settling_time,
     drying_time] = get_values(  # noqa: F821
        "pipette_type", "pipette_mount", "sample_number", "sample_volume",
        "bead_ratio", "elution_buffer_volume", "incubation_time",
        "settling_time", "drying_time"
    )

    mag_deck = protocol_context.load_module('magdeck', '1')
    mag_plate = mag_deck.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')
    output_plate = protocol_context.load_labware(
        'biorad_96_wellplate_200ul_pcr', '2', 'output plate')

    total_tips = sample_number*8
    tiprack_num = math.ceil(total_tips/96)
    slots = ['3', '5', '6', '7', '8', '9', '10', '11'][:tiprack_num]

    pip_range = pipette_type.split('_')[0]
    if pip_range == 'p1000':
        tip_name = 'opentrons_96_tiprack_1000ul'
    elif pip_range == 'p300' or pip_range == 'p50':
        tip_name = 'opentrons_96_tiprack_300ul'
    elif pip_range == 'p20':
        tip_name = 'opentrons_96_tiprack_20ul'
    else:
        tip_name = 'opentrons_96_tiprack_10ul'
    tipracks = [
        protocol_context.load_labware(tip_name, slot)
        for slot in slots
    ]

    pipette = protocol_context.load_instrument(
        pipette_type, pipette_mount, tip_racks=tipracks)
    plate_EtOH = protocol_context.load_labware('unknown_96_wellplate_2400ul', 6)



    reagent_container = protocol_context.load_labware(
        'nest_96_wellplate_200ul_flat', '4')
    liquid_waste = plate_EtOH.columns()[1]
    col_num = math.ceil(sample_number/8)
    samples = [col for col in mag_plate.rows()[0][:col_num]]
    output = [col for col in output_plate.rows()[0][:col_num]]

    # Define reagents and liquid waste
    beads = reagent_container.columns()[0]
    ethanol = plate_EtOH.wells()[0]
    elution_buffer = reagent_container.columns()[2]

    # Define bead and mix volume
    bead_volume = sample_volume*bead_ratio
    if bead_volume/2 > pipette.max_volume:
        mix_vol = pipette.max_volume
    else:
        mix_vol = bead_volume/2
    total_vol = bead_volume + sample_volume + 5

    # Mix beads and PCR samples
    for target in samples:
        pipette.pick_up_tip()
        pipette.transfer(bead_volume, beads, target, new_tip='never')
        pipette.mix(10, mix_vol, target)
        pipette.blow_out()
        pipette.drop_tip()

    # Incubate beads and PCR product at RT for 5 minutes
    protocol_context.delay(seconds=incubation_time)

    # Engagae MagDeck and incubate
    mag_deck.engage()
    protocol_context.delay(seconds=settling_time)

    # Remove supernatant from magnetic beads
    pipette.flow_rate.aspirate = 25
    pipette.flow_rate.dispense = 150
    for target in samples:
        pipette.transfer(total_vol, target, liquid_waste, blow_out=True)

    # Wash beads twice with 70% ethanol
    air_vol = pipette.max_volume * 0.1
    for cycle in range(2):
        for target in samples:
            pipette.transfer(200, ethanol, target, air_gap=air_vol,
                             new_tip='once')
        protocol_context.delay(seconds=1)
        for target in samples:
            pipette.transfer(200, target, liquid_waste, air_gap=air_vol)

    # Dry at RT
    protocol_context.delay(seconds=drying_time)

    # Disengage MagDeck
    mag_deck.disengage()

    # Mix beads with elution buffer
    if elution_buffer_volume/2 > pipette.max_volume:
        mix_vol = pipette.max_volume
    else:
        mix_vol = elution_buffer_volume/2
    for target in samples:
        pipette.pick_up_tip()
        pipette.transfer(elution_buffer_volume, elution_buffer, target, new_tip='never')
        pipette.mix(20, mix_vol, target)
        pipette.drop_tip()

    # Incubate at RT
    protocol_context.delay(seconds=5)

    # Engage MagDeck and remain engaged for DNA elution
    mag_deck.engage()
    protocol_context.delay(seconds=settling_time)

    # Transfer clean PCR product to a new well
    for target, dest in zip(samples, output):
        pipette.transfer(elution_buffer_volume, target, dest, blow_out=True)
