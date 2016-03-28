set nocompatible

set number
set relativenumber

filetype plugin off

set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
Plugin 'VundleVim/Vundle.vim'
Plugin 'scrooloose/nerdtree'
Plugin 'scrooloose/syntastic'
Plugin 'easymotion/vim-easymotion'
Plugin 'Valloric/YouCompleteMe'
call vundle#end()

filetype plugin indent on

set backup
set backupdir=/home/webapps/jiggly/.vim/temp/
set directory=/home/webapps/jiggly/.vim/temp/
set noundofile
set autochdir
set cindent
set shiftwidth=4
set tabstop=4
set guifont=Lucida_Console:h11

set statusline+=%#warningmsg#
set statusline+=%{SyntasticStatuslineFlag()}
set statusline+=%*

let g:syntastic_always_populate_loc_list = 1
let g:syntastic_auto_loc_list = 1
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0 

let mapleader=","
inoremap <Up> <NOP>
inoremap <Down> <NOP>
inoremap <left> <NOP>
inoremap <Right> <NOP>
noremap <Up> <NOP>
noremap <Down> <NOP>
noremap <left> <NOP>
noremap <Right> <NOP>
map <Leader> <Plug>(easymotion-prefix)

autocmd InsertEnter * :set norelativenumber
autocmd InsertLeave * :set relativenumber
