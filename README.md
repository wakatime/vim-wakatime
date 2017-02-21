vim-wakatime
============

Quantify your coding inside Vim.


Installation
------------

1. Install [Vundle](https://github.com/gmarik/vundle), the Vim plugin manager.

2. Using [Vundle](https://github.com/gmarik/vundle):<br />
  `echo "Bundle 'wakatime/vim-wakatime'" >> ~/.vimrc && vim +BundleInstall`

  or using [Pathogen](https://github.com/tpope/vim-pathogen):<br />
  `cd ~/.vim/bundle && git clone git://github.com/wakatime/vim-wakatime.git`

3. Enter your [api key](https://wakatime.com/settings#apikey), then press `enter`.

4. Use Vim like you normally do and your time will be tracked for you automatically.

5. Visit https://wakatime.com to see your logged time.

Note: WakaTime depends on [Python](http://www.python.org/getit/) being installed to work correctly.


Screen Shots
------------

![Project Overview](https://wakatime.com/static/img/ScreenShots/Screen-Shot-2016-03-21.png)


Configuring
-----------

To use a custom python binary:

    let g:wakatime_PythonBinary = '/usr/bin/python'

The default is to use `python` from your system PATH.

WakaTime plugins share a common config file `~/.wakatime.cfg` located in your user home directory with [these options](https://github.com/wakatime/wakatime#configuring) available.

Uninstalling
------------

Remove `Bundle 'wakatime/vim-wakatime'` from your `.vimrc` file, then delete your `~/.wakatime.cfg` config file.
