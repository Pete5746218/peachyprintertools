import unittest
import os
import sys
from StringIO import StringIO

from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from domain.configuration_manager import ConfigurationManager
from api.print_api import PrintAPI
import test_helpers


class PrintAPITests(unittest.TestCase, test_helpers.TestHelpers):


    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.DripBasedZAxis')
    @patch('api.print_api.SubLayerGenerator')
    def test_print_gcode_should_create_required_classes_and_start_it(self,
            mock_SubLayerGenerator, 
            mock_DripBasedZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_dripbasedzaxis = mock_DripBasedZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        test_config = self.default_config

        api = PrintAPI(test_config)
        api.print_gcode(gcode_path)

        mock_SubLayerGenerator.assert_called_with(
            fake_layers,
            test_config.options.sublayer_height_mm
            )

        mock_DripBasedZAxis.assert_called_with(
            drips_per_mm = test_config.dripper.drips_per_mm,
            initial_height = 0.0,
            sample_rate =  test_config.audio.input.sample_rate,
            bit_depth = test_config.audio.input.bit_depth
            )
        mock_AudioModulationLaserControl.assert_called_with(
            test_config.audio.output.sample_rate,
            test_config.audio.output.modulation_on_frequency,
            test_config.audio.output.modulation_off_frequency,
            )
        mock_GCodeReader.assert_called_with(gcode_path)
        mock_AudioWriter.assert_called_with(
            test_config.audio.output.sample_rate,
            test_config.audio.output.bit_depth,
            )
        mock_Transformer.assert_called_with(
            test_config.calibration.max_deflection,
            test_config.calibration.height,
            test_config.calibration.lower_points,
            test_config.calibration.upper_points,
            )
        mock_PathToAudio.assert_called_with(
            actual_samples_per_second,
            mock_transformer, 
            test_config.options.laser_thickness_mm
            )
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            mock_sublayergenerator,
            zaxis = mock_dripbasedzaxis,
            zaxis_control = None,
            status_call_back = None,
            max_lead_distance = test_config.dripper.max_lead_distance_mm,
            abort_on_error = True
            )

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.DripBasedZAxis')
    @patch('api.print_api.SubLayerGenerator')
    def test_verify_gcode_should_create_required_classes_and_start_it_and_return_errors(self,
            mock_SubLayerGenerator, 
            mock_DripBasedZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_dripbasedzaxis = mock_DripBasedZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value
        expected_errors = ['Some Error']
        mock_controller.get_status.return_value = {'errors':expected_errors}

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        test_config = self.default_config
        api = PrintAPI(test_config)
        api.verify_gcode(gcode_path)


        mock_SubLayerGenerator.assert_called_with(
            fake_layers,
            test_config.options.sublayer_height_mm
            )

        self.assertEquals(0, mock_DripBasedZAxis.call_count)
        mock_AudioModulationLaserControl.assert_called_with(
            test_config.audio.output.sample_rate,
            test_config.audio.output.modulation_on_frequency,
            test_config.audio.output.modulation_off_frequency,
            )
        mock_GCodeReader.assert_called_with(gcode_path)

        self.assertEquals(0, mock_AudioWriter.call_count)

        mock_Transformer.assert_called_with(
            test_config.calibration.max_deflection,
            test_config.calibration.height,
            test_config.calibration.lower_points,
            test_config.calibration.upper_points,
            )
        mock_PathToAudio.assert_called_with(
            actual_samples_per_second,
            mock_transformer, 
            test_config.options.laser_thickness_mm
            )
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            None,
            mock_sublayergenerator,
            zaxis = None,
            zaxis_control = None,
            status_call_back = None,
            max_lead_distance = test_config.dripper.max_lead_distance_mm,
            abort_on_error = False
            )

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.DripBasedZAxis')
    @patch('api.print_api.SubLayerGenerator')
    def test_print_gcode_should_not_print_sublayers_if_option_flase(self,
            mock_SubLayerGenerator, 
            mock_DripBasedZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_dripbasedzaxis = mock_DripBasedZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value
        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        api = PrintAPI(self.default_config)
        api.print_gcode(gcode_path, print_sub_layers = False)

        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            fake_layers,
            zaxis = mock_dripbasedzaxis,
            zaxis_control = None,
            status_call_back = None,
            max_lead_distance = self.default_config.dripper.max_lead_distance_mm,
            abort_on_error = True
            )

    def test_print_can_be_stopped_before_started(self):
        api = PrintAPI(self.default_config)
        api.stop()

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.DripBasedZAxis')
    def test_get_status_calls_controller_status(self, 
            mock_DripBasedZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,):
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_audiomodulationlasercontrol.actual_samples_per_second = 7
        mock_controller = mock_Controller.return_value


        api = PrintAPI(self.default_config)
        api.print_gcode("Spam")
        api.get_status()

        mock_controller.get_status.assert_called_with()

    @patch('api.print_api.Controller')
    @patch('api.print_api.PathToAudio')
    @patch('api.print_api.HomogenousTransformer')
    @patch('api.print_api.AudioWriter')
    @patch('api.print_api.GCodeReader')
    @patch('api.print_api.AudioModulationLaserControl')
    @patch('api.print_api.DripBasedZAxis')
    @patch('api.print_api.SubLayerGenerator')
    @patch('api.print_api.SerialZAxisControl')
    def test_print_gcode_should_create_serial_control_if_specified_in_config(self,
            mock_SerialZAxisControl,
            mock_SubLayerGenerator, 
            mock_DripBasedZAxis,
            mock_AudioModulationLaserControl,
            mock_GCodeReader,
            mock_AudioWriter,
            mock_Transformer,
            mock_PathToAudio,
            mock_Controller,
            ):
        gcode_path = "FakeFile"
        actual_samples_per_second = 7
        fake_layers = "Fake Layers"
        mock_dripbasedzaxis = mock_DripBasedZAxis.return_value
        mock_audiomodulationlasercontrol = mock_AudioModulationLaserControl.return_value
        mock_gcodereader = mock_GCodeReader.return_value
        mock_sublayergenerator = mock_SubLayerGenerator.return_value
        mock_audiowriter = mock_AudioWriter.return_value
        mock_transformer = mock_Transformer.return_value
        mock_pathtoaudio = mock_PathToAudio.return_value
        mock_controller = mock_Controller.return_value
        mock_serialzaxiscontrol = mock_SerialZAxisControl.return_value

        mock_audiomodulationlasercontrol.actual_samples_per_second = actual_samples_per_second
        mock_gcodereader.get_layers.return_value = fake_layers

        config = self.default_config
        config.serial.on = True
        config.serial.port = "COM6"
        config.serial.on_command = "ON"
        config.serial.off_command = "OFF"
        api = PrintAPI(config)
        api.print_gcode(gcode_path)

        mock_SerialZAxisControl.assert_called_with("COM6", on_command = "ON", off_command = "OFF")
        mock_Controller.assert_called_with(
            mock_audiomodulationlasercontrol,
            mock_pathtoaudio,
            mock_audiowriter,
            mock_sublayergenerator,
            zaxis = mock_dripbasedzaxis,
            zaxis_control = mock_serialzaxiscontrol,
            status_call_back = None,
            max_lead_distance = config.dripper.max_lead_distance_mm,
            abort_on_error = True
        )

if __name__ == '__main__':
    unittest.main()