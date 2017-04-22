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

4. Use Vim and your coding activity will be displayed on your [WakaTime dashboard](https://wakatime.com).

Note: WakaTime depends on [Python](http://www.python.org/getit/) being installed to work correctly.


Screen Shots
------------

![Project Overview](https://wakatime.com/static/img/ScreenShots/Screen-Shot-2016-03-21.png)


Configuring
-----------

To use a custom python binary:

    let g:wakatime_PythonBinary = '/usr/bin/python'

The default is to use `python` from your system PATH.

WakaTime plugins share a common config file `~/.wakatime.cfg` located in your user home directory with [these options][wakatime-cli-config] available.


Troubleshooting
---------------

Run `:WakaTimeDebugEnable` in Vim to see errors output in your status bar.
Enabling Debug Mode also writes verbose logs to `$WAKATIME_HOME/.wakatime.log` from [wakatime-cli][wakatime-cli].
With Debug Mode enabled, the plugin sends data synchronously so disable it when finished debugging.

The [How to Debug Plugins][how to debug] guide shows how to check when coding activity was last received from Vim use the [User Agents API][user agents api].
For more general troubleshooting info, see the [wakatime-cli Troubleshooting Section][wakatime-cli-help].


Uninstalling
------------

Remove `Bundle 'wakatime/vim-wakatime'` from your `.vimrc` file, then delete your `~/.wakatime.cfg` config file.


[wakatime-cli]: https://github.com/wakatime/wakatime
[wakatime-cli-config]: https://github.com/wakatime/wakatime#configuring
[wakatime-cli-help]: https://github.com/wakatime/wakatime#troubleshooting
[how to debug]: https://wakatime.com/faq#debug-plugins
[user agents api]: https://wakatime.com/developers#user_agents
