# vim-wakatime

[![Vim](https://wakatime.com/static/img/Vim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![Neovim](https://wakatime.com/static/img/Neovim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![MacVim](https://wakatime.com/static/img/MacVim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![gVim](https://wakatime.com/static/img/gVim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)

Quantify your coding inside Vim.


Installation
------------

1. Install [Vundle](https://github.com/gmarik/vundle), the Vim plugin manager.

2. Using [Vundle](https://github.com/gmarik/vundle):<br />
  `echo "Plugin 'wakatime/vim-wakatime'" >> ~/.vimrc && vim +PluginInstall`

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

#### Custom Commands:

* `:WakaTimeApiKey` - change the api key saved in your `~/.wakatime.cfg`
* `:WakaTimeDebugEnable` - enable debug mode (may slow down Vim so disable when finished debugging)
* `:WakaTimeDebugDisable` - disable debug mode
* `:WakaTimeScreenRedrawEnable` - enable screen redraw to prevent artifacts
* `:WakaTimeScreenRedrawEnableAuto` - redraw screen when plugin takes too long
* `:WakaTimeScreenRedrawDisable` - disable screen redraw for performance

#### Vimrc Settings:

    let g:wakatime_PythonBinary = '/usr/bin/python'

Tells the plugin to use a custom python binary.
The default is to use `python` from your system PATH.

#### WakaTime Settings:

Add this line to your `~/.wakatime.cfg` file to modify your screen redraw setting:

    vi_redraw = enabled

Enables redrawing the screen after sending heartbeats, to prevent screen artifacts in case a key was pressed while the plugin executed.
Valid values for `vi_redraw` are `enabled`, `auto`, and `disabled`.
Redraw settings are ignored with Vim 8.0+ with async support.

Other WakaTime plugins also share this `~/.wakatime.cfg` file. [See all configs...][wakatime-cli-config]


Troubleshooting
---------------

Run `:WakaTimeDebugEnable` in Vim then run this Terminal command:

`tail -f ~/.wakatime.log`

Enabling Debug Mode writes Vim Script errors to your Vim Status Bar and tells [wakatime-cli][wakatime-cli] to write verbose logs to `$WAKATIME_HOME/.wakatime.log`.

Debug mode can make it hard to find the real error because of all the extra logging, so also try disabling Debug Mode while tailing `~/.wakatime.log` and editing files in Vim.
With Debug Mode enabled, the plugin sends data synchronously so disable it when finished debugging with `:WakaTimeDebugDisable`.

The [How to Debug Plugins][how to debug] guide shows how to check when coding activity was last received from Vim use the [User Agents API][user agents api].
For more general troubleshooting info, see the [wakatime-cli Troubleshooting Section][wakatime-cli-help].


Uninstalling
------------

1. Remove `Plugin 'wakatime/vim-wakatime'` from your `.vimrc` file.

2. Run in terminal: `rm ~/.wakatime.*`.

3. Run in terminal: `vim +PluginClean`.


[wakatime-cli]: https://github.com/wakatime/wakatime
[wakatime-cli-config]: https://github.com/wakatime/wakatime#configuring
[wakatime-cli-help]: https://github.com/wakatime/wakatime#troubleshooting
[how to debug]: https://wakatime.com/faq#debug-plugins
[user agents api]: https://wakatime.com/developers#user_agents
