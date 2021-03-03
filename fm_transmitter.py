#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: FM radio transmitter
# Author: Yakimov Ivan
# Description: FM Stereo with RDS transmitter
# GNU Radio version: 3.7.13.5
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.wxgui import forms
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import math
import osmosdr
import pmt
import rds
import time
import wx


class fm_transmitter(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="FM radio transmitter")
        _icon_path = "D:\GNURadio\share\icons\hicolor\scalable/apps\gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.vol = vol = 0.91
        self.sub_gain = sub_gain = 2
        self.samp_rate = samp_rate = 420e3
        self.rds_gain = rds_gain = 0.18
        self.ps2 = ps2 = "music heals!"
        self.ps1 = ps1 = "DEMOS FM"
        self.power = power = 45
        self.pilot_gain = pilot_gain = 0.16
        self.outbuffer = outbuffer = 150000
        self.hardware_rate = hardware_rate = 2e6
        self.fm_max_dev = fm_max_dev = 75e3
        self.channel_widht = channel_widht = 120e3
        self.center_freq = center_freq = 1000*1e5
        self.audio_rate = audio_rate = 44100

        ##################################################
        # Blocks
        ##################################################
        _vol_sizer = wx.BoxSizer(wx.VERTICAL)
        self._vol_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_vol_sizer,
        	value=self.vol,
        	callback=self.set_vol,
        	label='VOLUME',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._vol_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_vol_sizer,
        	value=self.vol,
        	callback=self.set_vol,
        	minimum=0,
        	maximum=1,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_vol_sizer)
        _sub_gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._sub_gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_sub_gain_sizer,
        	value=self.sub_gain,
        	callback=self.set_sub_gain,
        	label='L-R level ',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._sub_gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_sub_gain_sizer,
        	value=self.sub_gain,
        	callback=self.set_sub_gain,
        	minimum=0,
        	maximum=2,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_sub_gain_sizer)
        _rds_gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._rds_gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_rds_gain_sizer,
        	value=self.rds_gain,
        	callback=self.set_rds_gain,
        	label='RDS power',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._rds_gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_rds_gain_sizer,
        	value=self.rds_gain,
        	callback=self.set_rds_gain,
        	minimum=0,
        	maximum=0.2,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_rds_gain_sizer)
        self._ps2_text_box = forms.text_box(
        	parent=self.GetWin(),
        	value=self.ps2,
        	callback=self.set_ps2,
        	label='PS2',
        	converter=forms.str_converter(),
        )
        self.Add(self._ps2_text_box)
        self._ps1_text_box = forms.text_box(
        	parent=self.GetWin(),
        	value=self.ps1,
        	callback=self.set_ps1,
        	label='PS1',
        	converter=forms.str_converter(),
        )
        self.Add(self._ps1_text_box)
        _power_sizer = wx.BoxSizer(wx.VERTICAL)
        self._power_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_power_sizer,
        	value=self.power,
        	callback=self.set_power,
        	label='TX power',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._power_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_power_sizer,
        	value=self.power,
        	callback=self.set_power,
        	minimum=1,
        	maximum=47,
        	num_steps=46,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_power_sizer)
        _pilot_gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._pilot_gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_pilot_gain_sizer,
        	value=self.pilot_gain,
        	callback=self.set_pilot_gain,
        	label='Pilot tone 19KHz',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._pilot_gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_pilot_gain_sizer,
        	value=self.pilot_gain,
        	callback=self.set_pilot_gain,
        	minimum=0,
        	maximum=0.2,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_pilot_gain_sizer)
        _center_freq_sizer = wx.BoxSizer(wx.VERTICAL)
        self._center_freq_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_center_freq_sizer,
        	value=self.center_freq,
        	callback=self.set_center_freq,
        	label='F',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._center_freq_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_center_freq_sizer,
        	value=self.center_freq,
        	callback=self.set_center_freq,
        	minimum=880*1e5,
        	maximum=1080*1e5,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_center_freq_sizer)
        self.rational_resampler_xxx_4_0 = filter.rational_resampler_fff(
                interpolation=int(channel_widht/1000),
                decimation=380,
                taps=None,
                fractional_bw=None,
        )
        (self.rational_resampler_xxx_4_0).set_min_output_buffer(150000)
        self.rational_resampler_xxx_3_1 = filter.rational_resampler_fff(
                interpolation=int(channel_widht)/100,
                decimation=int(audio_rate)/100,
                taps=None,
                fractional_bw=None,
        )
        (self.rational_resampler_xxx_3_1).set_min_output_buffer(150000)
        self.rational_resampler_xxx_2 = filter.rational_resampler_ccc(
                interpolation=int(hardware_rate/10000),
                decimation=int(samp_rate/10000),
                taps=None,
                fractional_bw=None,
        )
        (self.rational_resampler_xxx_2).set_min_output_buffer(100000)
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=int(channel_widht/100),
                decimation=int(audio_rate/100),
                taps=None,
                fractional_bw=None,
        )
        (self.rational_resampler_xxx_1).set_min_output_buffer(150000)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=int(samp_rate/1000),
                decimation=int(channel_widht/1000),
                taps=None,
                fractional_bw=None,
        )
        (self.rational_resampler_xxx_0).set_min_output_buffer(150000)
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + 'hackrf' )
        self.osmosdr_sink_0.set_sample_rate(hardware_rate)
        self.osmosdr_sink_0.set_center_freq(center_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(0, 0)
        self.osmosdr_sink_0.set_if_gain(power, 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(1.75e6, 0)

        self.gr_unpack_k_bits_bb_0_0 = blocks.unpack_k_bits_bb(2)
        (self.gr_unpack_k_bits_bb_0_0).set_max_output_buffer(150000)
        self.gr_sig_source_x_0_0_0 = analog.sig_source_f(channel_widht, analog.GR_SIN_WAVE, 57e3, rds_gain, 0)
        (self.gr_sig_source_x_0_0_0).set_min_output_buffer(150000)
        self.gr_rds_encoder_0_0 = rds.encoder(0, 11, True, ps1, 96900000,
        			False, False, 7, 0,
        			000, ps2)

        (self.gr_rds_encoder_0_0).set_max_output_buffer(150000)
        self.gr_multiply_xx_0_0 = blocks.multiply_vff(1)
        (self.gr_multiply_xx_0_0).set_min_output_buffer(150000)
        self.gr_map_bb_1_0 = digital.map_bb(([1,2]))
        (self.gr_map_bb_1_0).set_max_output_buffer(150000)
        self.gr_map_bb_0_0 = digital.map_bb(([-1,1]))
        (self.gr_map_bb_0_0).set_max_output_buffer(150000)
        self.gr_frequency_modulator_fc_0 = analog.frequency_modulator_fc(2*math.pi*fm_max_dev/samp_rate*0.6)
        (self.gr_frequency_modulator_fc_0).set_min_output_buffer(150000)
        self.gr_diff_encoder_bb_0_0 = digital.diff_encoder_bb(2)
        (self.gr_diff_encoder_bb_0_0).set_max_output_buffer(150000)
        self.gr_char_to_float_0_0 = blocks.char_to_float(1, 1)
        (self.gr_char_to_float_0_0).set_max_output_buffer(150000)
        self.gr_add_xx_0_0_0_1 = blocks.add_vff(1)
        (self.gr_add_xx_0_0_0_1).set_min_output_buffer(150000)
        self.fir_filter_xxx_2 = filter.fir_filter_fff(1, (firdes.low_pass(1, channel_widht, 2.4e3, 0.5e3)))
        self.fir_filter_xxx_2.declare_sample_delay(0)
        (self.fir_filter_xxx_2).set_min_output_buffer(150000)
        self.fir_filter_xxx_1 = filter.fir_filter_fff(1, (firdes.low_pass(2, audio_rate, 16e3, 0.2e3) ))
        self.fir_filter_xxx_1.declare_sample_delay(0)
        (self.fir_filter_xxx_1).set_min_output_buffer(150000)
        self.fir_filter_xxx_0 = filter.fir_filter_fff(1, (firdes.low_pass(1, audio_rate, 16e3, 1e3)))
        self.fir_filter_xxx_0.declare_sample_delay(0)
        (self.fir_filter_xxx_0).set_min_output_buffer(150000)
        self.blocks_sub_xx_0_0 = blocks.sub_ff(1)
        (self.blocks_sub_xx_0_0).set_min_output_buffer(150000)
        self.blocks_short_to_float_1 = blocks.short_to_float(1, 1)
        self.blocks_short_to_float_0 = blocks.short_to_float(1, 1)
        self.blocks_repeat_0_0 = blocks.repeat(gr.sizeof_float*1, 160)
        (self.blocks_repeat_0_0).set_min_output_buffer(150000)
        self.blocks_multiply_xx_1_0 = blocks.multiply_vff(1)
        (self.blocks_multiply_xx_1_0).set_min_output_buffer(150000)
        self.blocks_multiply_const_xx_0_0 = blocks.multiply_const_ff(0.000032)
        (self.blocks_multiply_const_xx_0_0).set_min_output_buffer(150000)
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_ff(0.000032)
        (self.blocks_multiply_const_xx_0).set_min_output_buffer(150000)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vff((vol, ))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((vol, ))
        self.blocks_keep_m_in_n_0_0 = blocks.keep_m_in_n(gr.sizeof_short, 1, 2, 1)
        (self.blocks_keep_m_in_n_0_0).set_min_output_buffer(150000)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_short, 1, 2, 0)
        (self.blocks_keep_m_in_n_0).set_min_output_buffer(150000)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_short*1, 'C:\\Users\\denim\\Music\\1.wav', True)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        (self.blocks_file_source_0).set_min_output_buffer(50000)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, 200000)
        (self.blocks_delay_0).set_min_output_buffer(150000)
        self.blocks_add_xx_2 = blocks.add_vff(1)
        (self.blocks_add_xx_2).set_min_output_buffer(150000)
        self.analog_sig_source_x_1_1 = analog.sig_source_f(channel_widht, analog.GR_SIN_WAVE, 19e3, pilot_gain, 0)
        (self.analog_sig_source_x_1_1).set_min_output_buffer(150000)
        self.analog_sig_source_x_1_0_0 = analog.sig_source_f(channel_widht, analog.GR_SIN_WAVE, 38e3, sub_gain, 0)
        (self.analog_sig_source_x_1_0_0).set_min_output_buffer(150000)
        self.analog_fm_preemph_0_0_0_0_0 = analog.fm_preemph(fs=audio_rate, tau=50e-6, fh=-1.0)
        (self.analog_fm_preemph_0_0_0_0_0).set_min_output_buffer(150000)
        self.analog_fm_preemph_0_0_0_0 = analog.fm_preemph(fs=audio_rate, tau=50e-6, fh=-1.0)
        (self.analog_fm_preemph_0_0_0_0).set_min_output_buffer(150000)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fm_preemph_0_0_0_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.analog_fm_preemph_0_0_0_0_0, 0), (self.fir_filter_xxx_1, 0))
        self.connect((self.analog_sig_source_x_1_0_0, 0), (self.blocks_multiply_xx_1_0, 1))
        self.connect((self.analog_sig_source_x_1_1, 0), (self.blocks_add_xx_2, 0))
        self.connect((self.blocks_add_xx_2, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_keep_m_in_n_0_0, 0))
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.blocks_short_to_float_0, 0))
        self.connect((self.blocks_keep_m_in_n_0_0, 0), (self.blocks_short_to_float_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_multiply_const_xx_0_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.blocks_sub_xx_0_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.gr_add_xx_0_0_0_1, 0))
        self.connect((self.blocks_multiply_const_xx_0_0, 0), (self.blocks_sub_xx_0_0, 1))
        self.connect((self.blocks_multiply_const_xx_0_0, 0), (self.gr_add_xx_0_0_0_1, 1))
        self.connect((self.blocks_multiply_xx_1_0, 0), (self.blocks_add_xx_2, 2))
        self.connect((self.blocks_repeat_0_0, 0), (self.rational_resampler_xxx_4_0, 0))
        self.connect((self.blocks_short_to_float_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_short_to_float_1, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_sub_xx_0_0, 0), (self.analog_fm_preemph_0_0_0_0_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.analog_fm_preemph_0_0_0_0, 0))
        self.connect((self.fir_filter_xxx_1, 0), (self.rational_resampler_xxx_3_1, 0))
        self.connect((self.fir_filter_xxx_2, 0), (self.gr_multiply_xx_0_0, 1))
        self.connect((self.gr_add_xx_0_0_0_1, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.gr_char_to_float_0_0, 0), (self.blocks_repeat_0_0, 0))
        self.connect((self.gr_diff_encoder_bb_0_0, 0), (self.gr_map_bb_1_0, 0))
        self.connect((self.gr_frequency_modulator_fc_0, 0), (self.rational_resampler_xxx_2, 0))
        self.connect((self.gr_map_bb_0_0, 0), (self.gr_char_to_float_0_0, 0))
        self.connect((self.gr_map_bb_1_0, 0), (self.gr_unpack_k_bits_bb_0_0, 0))
        self.connect((self.gr_multiply_xx_0_0, 0), (self.blocks_add_xx_2, 3))
        self.connect((self.gr_rds_encoder_0_0, 0), (self.gr_diff_encoder_bb_0_0, 0))
        self.connect((self.gr_sig_source_x_0_0_0, 0), (self.gr_multiply_xx_0_0, 0))
        self.connect((self.gr_unpack_k_bits_bb_0_0, 0), (self.gr_map_bb_0_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.gr_frequency_modulator_fc_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.blocks_add_xx_2, 1))
        self.connect((self.rational_resampler_xxx_2, 0), (self.blocks_delay_0, 0))
        self.connect((self.rational_resampler_xxx_3_1, 0), (self.blocks_multiply_xx_1_0, 0))
        self.connect((self.rational_resampler_xxx_4_0, 0), (self.fir_filter_xxx_2, 0))

    def get_vol(self):
        return self.vol

    def set_vol(self, vol):
        self.vol = vol
        self._vol_slider.set_value(self.vol)
        self._vol_text_box.set_value(self.vol)
        self.blocks_multiply_const_vxx_0_0.set_k((self.vol, ))
        self.blocks_multiply_const_vxx_0.set_k((self.vol, ))

    def get_sub_gain(self):
        return self.sub_gain

    def set_sub_gain(self, sub_gain):
        self.sub_gain = sub_gain
        self._sub_gain_slider.set_value(self.sub_gain)
        self._sub_gain_text_box.set_value(self.sub_gain)
        self.analog_sig_source_x_1_0_0.set_amplitude(self.sub_gain)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.gr_frequency_modulator_fc_0.set_sensitivity(2*math.pi*self.fm_max_dev/self.samp_rate*0.6)

    def get_rds_gain(self):
        return self.rds_gain

    def set_rds_gain(self, rds_gain):
        self.rds_gain = rds_gain
        self._rds_gain_slider.set_value(self.rds_gain)
        self._rds_gain_text_box.set_value(self.rds_gain)
        self.gr_sig_source_x_0_0_0.set_amplitude(self.rds_gain)

    def get_ps2(self):
        return self.ps2

    def set_ps2(self, ps2):
        self.ps2 = ps2
        self._ps2_text_box.set_value(self.ps2)

    def get_ps1(self):
        return self.ps1

    def set_ps1(self, ps1):
        self.ps1 = ps1
        self._ps1_text_box.set_value(self.ps1)
        self.gr_rds_encoder_0_0.set_ps(self.ps1)

    def get_power(self):
        return self.power

    def set_power(self, power):
        self.power = power
        self._power_slider.set_value(self.power)
        self._power_text_box.set_value(self.power)
        self.osmosdr_sink_0.set_if_gain(self.power, 0)

    def get_pilot_gain(self):
        return self.pilot_gain

    def set_pilot_gain(self, pilot_gain):
        self.pilot_gain = pilot_gain
        self._pilot_gain_slider.set_value(self.pilot_gain)
        self._pilot_gain_text_box.set_value(self.pilot_gain)
        self.analog_sig_source_x_1_1.set_amplitude(self.pilot_gain)

    def get_outbuffer(self):
        return self.outbuffer

    def set_outbuffer(self, outbuffer):
        self.outbuffer = outbuffer

    def get_hardware_rate(self):
        return self.hardware_rate

    def set_hardware_rate(self, hardware_rate):
        self.hardware_rate = hardware_rate
        self.osmosdr_sink_0.set_sample_rate(self.hardware_rate)

    def get_fm_max_dev(self):
        return self.fm_max_dev

    def set_fm_max_dev(self, fm_max_dev):
        self.fm_max_dev = fm_max_dev
        self.gr_frequency_modulator_fc_0.set_sensitivity(2*math.pi*self.fm_max_dev/self.samp_rate*0.6)

    def get_channel_widht(self):
        return self.channel_widht

    def set_channel_widht(self, channel_widht):
        self.channel_widht = channel_widht
        self.gr_sig_source_x_0_0_0.set_sampling_freq(self.channel_widht)
        self.fir_filter_xxx_2.set_taps((firdes.low_pass(1, self.channel_widht, 2.4e3, 0.5e3)))
        self.analog_sig_source_x_1_1.set_sampling_freq(self.channel_widht)
        self.analog_sig_source_x_1_0_0.set_sampling_freq(self.channel_widht)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self._center_freq_slider.set_value(self.center_freq)
        self._center_freq_text_box.set_value(self.center_freq)
        self.osmosdr_sink_0.set_center_freq(self.center_freq, 0)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.fir_filter_xxx_1.set_taps((firdes.low_pass(2, self.audio_rate, 16e3, 0.2e3) ))
        self.fir_filter_xxx_0.set_taps((firdes.low_pass(1, self.audio_rate, 16e3, 1e3)))


def main(top_block_cls=fm_transmitter, options=None):

    tb = top_block_cls()
    tb.Start(True)
    tb.Wait()


if __name__ == '__main__':
    main()
