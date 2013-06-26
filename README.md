vim-wakatime 0.1.2
===========

Automatic time tracking.

Installation
------------

1) Get an api key from:

https://wakati.me

2) Using [Vundle](https://github.com/gmarik/vundle), the Vim plugin manager:

Add `Bundle 'wakatime/vim-wakatime'` to your `~/.vimrc`

3) Run these shell commands:

    touch ~/.wakatime.log
    echo "api_key=MY_API_KEY" > ~/.wakatime
    vim +BundleInstall +qall

4) Use Vim and your time will automatically be tracked for you.

Visit https://wakati.me to view your time spent in each file.

Screen Shots
------------

![Project Overview](https://www.wakati.me/static/img/ScreenShots/Screenshot%20from%202013-06-26%2001:12:59.png)

![Files in a Project](https://www.wakati.me/static/img/ScreenShots/Screenshot%20from%202013-06-26%2001:13:13.png)

![Changing Date Range](https://www.wakati.me/static/img/ScreenShots/Screenshot%20from%202013-06-26%2001:13:53.png)

