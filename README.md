vim-wakatime 0.1.2
===========

Automatic time tracking.

Installation
------------

1) Get an api key from:

https://www.wakati.me

2) Using [Vundle](https://github.com/gmarik/vundle), the Vim plugin manager:

Add `Bundle 'wakatime/vim-wakatime'` to your `~/.vimrc`

3) Run these shell commands:

    sudo touch /var/log/wakatime.log && sudo chmod a+w !$
    echo "api_key=MY_API_KEY" > ~/.wakatime
    vim +BundleInstall +qall

