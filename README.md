# vim-wakatime

[![Vim](https://wakatime.com/static/img/Vim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![Neovim](https://wakatime.com/static/img/Neovim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![MacVim](https://wakatime.com/static/img/MacVim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![gVim](https://wakatime.com/static/img/gVim-supported-brightgreen.svg)](https://github.com/wakatime/vim-wakatime#installation)
[![Coding time tracker](https://wakatime.com/badge/github/wakatime/vim-wakatime.svg)](https://wakatime.com/badge/github/wakatime/vim-wakatime)

[WakaTime][wakatime] is an open source Vim plugin for metrics, insights, and time tracking automatically generated from your programming activity.

## Installation

1. With [Vundle](https://github.com/gmarik/vundle): `echo "Plugin 'wakatime/vim-wakatime'" >> ~/.vimrc && vim +PluginInstall`

   Or with [Pathogen](https://github.com/tpope/vim-pathogen): `cd ~/.vim/bundle && git clone git://github.com/wakatime/vim-wakatime.git`

   Or with [Vim-plug](https://github.com/junegunn/vim-plug):  add `Plug 'wakatime/vim-wakatime'` to .vimrc file. While in vim reload .vimrc with `:so ~/.vimrc` or restart vim, enter
    `:PlugInstall`
    
   Or with [Packer](https://github.com/wbthomason/packer.nvim): add `use 'wakatime/vim-wakatime'` to your plugins file.

2. Enter your [api key](https://wakatime.com/settings#apikey), then press `enter`.

3. Use Vim and your coding activity will be displayed on your [WakaTime dashboard](https://wakatime.com).


## Screen Shots

![Project Overview](https://wakatime.com/static/img/ScreenShots/Screen-Shot-2016-03-21.png)


## Configuring

#### Commands:

* `:WakaTimeApiKey` - change the api key saved in your `~/.wakatime.cfg`
* `:WakaTimeDebugEnable` - enable debug mode (may slow down Vim so disable when finished debugging)
* `:WakaTimeDebugDisable` - disable debug mode
* `:WakaTimeScreenRedrawEnable` - enable screen redraw to prevent artifacts (only for Vim < 8.0)
* `:WakaTimeScreenRedrawEnableAuto` - redraw screen when plugin takes too long (only for Vim < 8.0)
* `:WakaTimeScreenRedrawDisable` - disable screen redraw
* `:WakaTimeToday` - echo your total coding activity for Today

The vim-wakatime plugin automatically downloads and updates [wakatime-cli][wakatime-cli] in your `$WAKATIME_HOME/.wakatime/` folder.
WakaTime plugins also share a common [$WAKATIME_HOME/.wakatime.cfg config file][wakatime-cli-config].
`$WAKATIME_HOME` defaults to your `$HOME` folder.


## Troubleshooting

Run `:WakaTimeDebugEnable` in Vim then run this Terminal command:

`tail -f ~/.wakatime.log`

Enabling Debug Mode writes Vim Script errors to your Vim Status Bar and tells [wakatime-cli][wakatime-cli] to write verbose logs to `$WAKATIME_HOME/.wakatime.log`.

Debug mode can make it hard to find the real error because of all the extra logging, so also try disabling Debug Mode while tailing `~/.wakatime.log` and editing files in Vim.
With Debug Mode enabled, the plugin sends data synchronously so disable it when finished debugging with `:WakaTimeDebugDisable`.

The [How to Debug Plugins][how to debug] guide shows how to check when coding activity was last received from Vim use the [User Agents API][user agents api].
For more general troubleshooting info, see the [wakatime-cli Troubleshooting Section][wakatime-cli-help].

It is also worth noting that if the [Go CLI](https://github.com/wakatime/wakatime-cli) isn't present, it will fall back to the [Legacy Python CLI](https://github.com/wakatime/legacy-python-cli) if it's available, without warning. If you get an error that appears to be from the Python CLI, consider moving over to the Go CLI to relieve said errors.

## Uninstalling

1. Remove `Plugin 'wakatime/vim-wakatime'` from your `.vimrc` file.

2. Run in terminal: `rm ~/.wakatime.*`.

3. Run in terminal: `vim +PluginClean`.

**_If using vim-plug_**

_While in vim_

1. Delete or comment out `Plug` command from .vimrc file.

2. Reload vimrc (`:so ~/.vimrc`) or restart vim

3. Run `:PlugClean`, it will detect and remove undeclared plugins.

[wakatime]: https://wakatime.com/vim
[wakatime-cli]: https://github.com/wakatime/wakatime-cli
[wakatime-cli-config]: https://github.com/wakatime/wakatime-cli/blob/develop/USAGE.md#ini-config-file
[wakatime-cli-help]: https://github.com/wakatime/wakatime#troubleshooting
[how to debug]: https://wakatime.com/faq#debug-plugins
[user agents api]: https://wakatime.com/developers#user_agents
