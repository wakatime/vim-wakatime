vim-wakatime 0.1.2
===========

Automatic time tracking.

Installation
------------

Get an api key by signing up at https://www.wakati.me

Using [Vundle](https://github.com/gmarik/vundle), the Vim plugin manager:

Add `Bundle 'wakatime/vim-wakatime' to your `~/.vimrc`

Then run these shell commands:

    sudo touch /var/log/wakatime.log
    echo "api_key=MY_API_KEY" > ~/.wakatime
    vim +BundleInstall +qall

