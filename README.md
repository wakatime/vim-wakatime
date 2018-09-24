[![Vim](https://wakatime.com/static/img/Vim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![Neovim](https://wakatime.com/static/img/Neovim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![MacVim](https://wakatime.com/static/img/MacVim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![gVim](https://wakatime.com/static/img/gVim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)


# vim-wakatime

Quantify your coding inside Vim.


Installation
------------

1. With [Vundle](https://github.com/gmarik/vundle): `echo "Plugin 'wakatime/vim-wakatime'" >> ~/.vimrc && vim +PluginInstall`

   Or with [Pathogen](https://github.com/tpope/vim-pathogen): `cd ~/.vim/bundle && git clone git://github.com/wakatime/vim-wakatime.git`

   Or with [Vim-plug](https://github.com/junegunn/vim-plug):  add `Plug 'wakatime/vim-wakatime'` to .vimrc file. While in vim reload .vimrc with `:so ~/.vimrc` or restart vim, enter
    `:PlugInstall`.

2. Enter your [api key](https://wakatime.com/settings#apikey), then press `enter`. 

3. Use Vim and your coding activity will be displayed on your [WakaTime dashboard](https://wakatime.com).

Note: WakaTime depends on [Python](http://www.python.org/getit/) being installed to work correctly.


Screen Shots
------------

![Project Overview](https://wakatime.com/static/img/ScreenShots/Screen-Shot-2016-03-21.png)


Configuring
-----------

#### Commands:

* `:WakaTimeApiKey` - change the api key saved in your `~/.wakatime.cfg`
* `:WakaTimeDebugEnable` - enable debug mode (may slow down Vim so disable when finished debugging)
* `:WakaTimeDebugDisable` - disable debug mode
* `:WakaTimeScreenRedrawEnable` - enable screen redraw to prevent artifacts (only for Vim < 8.0)
* `:WakaTimeScreenRedrawEnableAuto` - redraw screen when plugin takes too long (only for Vim < 8.0)
* `:WakaTimeScreenRedrawDisable` - disable screen redraw

#### Vimrc Settings:

    let g:wakatime_PythonBinary = '/usr/bin/python'  " (Default: 'python')

Tells the plugin to use a custom python binary.
The default is to use `python` from your system PATH.

    let g:wakatime_OverrideCommandPrefix = '/usr/bin/wakatime'  " (Default: '')

Overrides the WakaTime CLI command prefix. You might need this when running
[wakatime-cli][wakatime-cli] with a custom wrapper script or from the pip
installed binary. Normally, the bundled [wakatime-cli][wakatime-cli] is used
so this setting is not needed.

WakaTime plugins also share a common `~/.wakatime.cfg` config file. [See common configs...][wakatime-cli-config]


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

**_If using vim-plug_**

_While in vim_

1. Delete or comment out `Plug` command from .vimrc file.

2. Reload vimrc (`:so ~/.vimrc`) or restart vim

3. Run `:PlugClean`, it will detect and remove undeclared plugins.

[wakatime-cli]: https://github.com/wakatime/wakatime
[wakatime-cli-config]: https://github.com/wakatime/wakatime#configuring
[wakatime-cli-help]: https://github.com/wakatime/wakatime#troubleshooting
[how to debug]: https://wakatime.com/faq#debug-plugins
[user agents api]: https://wakatime.com/developers#user_agents
