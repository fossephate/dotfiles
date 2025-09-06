brew tap FelixKratz/formulae
brew install borders

# brew install sketchybar

brew uninstall sketchybar
brew tap fossephate/formulae
brew install --HEAD sketchybar-display

brew tap leoafarias/fvm
brew install fvm

brew install nvm
brew install pnpm
brew install deno
brew install imagemagick
brew install swiftformat
brew install starship

brew install --cask orion
brew install --cask xcodes
brew install --cask slack
brew install --cask discord
brew install --cask spotify
brew install --cask arc
brew install --cask 1password
brew install --cask warp
brew install --cask karabiner-elements
brew install --cask cursor
brew install --cask raycast
brew install --cask menuwhere
brew install --cask homerow
brew install --cask wezterm
brew install --cask ghostty
brew install --cask shottr
brew install --cask aldente
brew install --cask copyclip
brew install --cask crossover
brew install --cask cleanshot
brew install --cask gitkraken

# starship font
brew install --cask font-fira-code-nerd-font
brew install --cask font-sf-mono-nerd-font-ligaturized
starship preset gruvbox-rainbow -o ~/.config/starship.toml

brew install --cask nikitabobko/tap/aerospace
brew install --cask mouseless


# scutil --get HostName 
scutil --set LocalHostName book
scutil --set ComputerName book

# https://sindresorhus.com/supercharge
# https://dropoverapp.com
# picasso app mac app store