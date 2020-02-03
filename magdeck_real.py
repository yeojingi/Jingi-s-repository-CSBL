from opentrons import protocol_api

metadata = {'apiLevel': '2.0'}

def run(protocol: protocol_api.ProtocolContext):
    volume_of_PCR_product = 20 #micro liter
    rate_of_bead_to_product = 0.85

    mag_mod = protocol.load_module('magnetic module', '1')
    plate_on_mag = mag_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')
    # The code from the rest of the examples in this section goes here
    tiprack_single = protocol.load_labware('opentrons_96_tiprack_300ul', 3)
    tiprack_multi = protocol.load_labware('opentrons_96_tiprack_300ul', 6)
    plate_center = protocol.load_labware('nest_96_wellplate_200ul_flat', 5)
    plate_rack_7 = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', 7)
    plate_EtOH = protocol.load_labware('nest_96_wellplate_200ul_flat', 2)
    plate_rack_bead = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 4)

    pipette_left_single_p300 = protocol.load_instrument('p300_single', 'left', tip_racks=[tiprack_single])
    pipette_right_multi_p50 = protocol.load_instrument('p50_multi', 'right', tip_racks=[tiprack_multi])

#    mag_mod.engage()
#    protocol.delay(seconds = 20)
#    mag_mod.disengage()

#modify if it is dealing with mass products later
 #   pipette_left_single_p300.transfer(volume_of_PCR_product*0.85, plate_rack_bead['A1'].bottom(z=15), plate_center.columns()[0])

    #1번 bead를 PCR product와 섞어 준다.
    pipette_left_single_p300.transfer(volume_of_PCR_product*rate_of_bead_to_product, plate_rack_bead['A1'], plate_on_mag['A1'])

    #나중엔 multi 로
    #2번
    pipette_left_single_p300.pick_up_tip()
    pipette_left_single_p300.mix(20, volume_of_PCR_product + volume_of_PCR_product*rate_of_bead_to_product, plate_on_mag['A1'], 1)
    pipette_left_single_p300.drop_tip()

    #3버
    #protocol.delay(minutes = 5) #원래는 5분
    protocol.comment("Incubation for 5 minutes")
    protocol.delay(seconds=5)

    #4번
    mag_mod.engage()
    #protocol.delay(minutes = 5)
    protocol.delay(seconds=5)

    #5번
    #EtOH 제작은 생략

    #6번
    pipette_left_single_p300.pick_up_tip()
    pipette_left_single_p300.speed.aspirate = 50
    pipette_left_single_p300.aspirate(volume_of_PCR_product + volume_of_PCR_product*rate_of_bead_to_product, plate_on_mag['A1'])
    pipette_left_single_p300.speed.aspirate = 150
    pipette_left_single_p300.drop_tip()

    #7~8번 벽에 붙어서 하도록 위치 조정 필요

    #7번
    #multi later
    pipette_left_single_p300.transfer(200, plate_EtOH['A1'], plate_on_mag['A1'])
    #protocol.delay(seconds=30)
    pipette_left_single_p300.pick_up_tip()
    pipette_left_single_p300.speed.aspirate = 50
    pipette_left_single_p300.aspirate(200, plate_on_mag['A1'])
    pipette_left_single_p300.speed.aspirate = 150
    pipette_left_single_p300.drop_tip()

    #8번
    #multi later
    pipette_left_single_p300.transfer(200, plate_EtOH['A1'], plate_on_mag['A1'])
    #protocol.delay(seconds=30)
    pipette_left_single_p300.pick_up_tip()
    pipette_left_single_p300.speed.aspirate = 50
    pipette_left_single_p300.aspirate(200, plate_on_mag['A1'])
    pipette_left_single_p300.speed.aspirate = 150
    pipette_left_single_p300.drop_tip()

    #9번
#    protocol.delay(minutes= 7)
    protocol.delay(seconds = 8)

    #10번