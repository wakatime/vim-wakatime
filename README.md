vim-wakatime
============

Fully automatic time tracking for Vim.


Installation
------------

Heads Up! WakaTime depends on [Python](http://www.python.org/getit/) being installed to work correctly.

1. Get an api key from: https://wakatime.com/#apikey

2. Using [Vundle](https://github.com/gmarik/vundle), the Vim plugin manager:<br />
  `echo "Bundle 'wakatime/vim-wakatime'" >> ~/.vimrc && vim +BundleInstall`

  or using [Pathogen](https://github.com/tpope/vim-pathogen):<br />
  `cd ~/.vim/bundle && git clone git://github.com/wakatime/vim-wakatime.git`

3. You will see a prompt at the bottom asking for your [api key](https://wakatime.com/#apikey). Enter your api key, then press `enter`.

4. Use Vim and your time will automatically be tracked for you.

5. Visit https://wakatime.com to see your logged time.

6. Consider installing [BIND9](https://help.ubuntu.com/community/BIND9ServerHowto#Caching_Server_configuration) to cache your repeated DNS requests: `sudo apt-get install bind9`


Screen Shots
------------

![Project Overview](https://wakatime.com/static/img/ScreenShots/Screen Shot 2013-10-26 at 5.04.01 PM.png)
