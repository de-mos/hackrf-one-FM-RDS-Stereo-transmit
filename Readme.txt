Stereo Audio Source - FIX 2 chanel Sound Card


I followed these steps:

1.- Check the audio module used by GNU Radio using the command:

C:\GNURadio-3.7\bin> gnuradio-config-info --prefs

The command showed (among other preferences):

[audio]
audio_module = auto
...
...

2.- Obtain the location of the GNU Radio user preferences directory using the command:

C:\GNURadio-3.7\bin> gnuradio-config-info --userprefs

In my case that directory was:

C:\Users\AppData\Roaming\.gnuradio

3.- Go to that directory and create there a file named 'config.conf' containing:

[audio]
audio_module = portaudio

4.- Repeat step 1 to check the change in the audio module used by GNU Radio:

[audio]
audio_module = portaudio
...
...

And that's all: after restarting GNU Radio Companion, Audio Source can now use 2 output channels.