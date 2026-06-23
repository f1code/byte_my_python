Title: Switching to the Kitty Terminal Emulator
Date: 2026-06-23
Modified: 2026-06-23
Category: Tools
Tags: kitty, terminal, ghostty, zellij, productivity

This weekend I moved from Ghostty + Zellij to Kitty.

The main reason I wanted to drop Zellij was the overhead—especially in terms of memory (Ghostty regularly got up to 8GB of RAM, thanks to it). But there were still a few things missing when using Ghostty without Zellij... Customizing the click action for example was very difficult (in Zellij you can make a plugin to customize that, and I did one to be able to match the links in a way that fit my workflow better—[miserly-link](https://github.com/f1code/miserly-link)).

I tried another terminal, Kitty. You could say Ghostty is actually greatly inspired by Kitty which introduced extensions to the terminal such as the [Kitty Image Protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/). Kitty is (like Ghostty) very fast, but is a bit more mature so it has many more features. A lot of the features are very keyboard-centric which I love.

## Quick start and config

Unlike Ghostty which starts with a barebone config, Kitty ships with a very long config file with most of the defaults commented out.

A lot of the shortcuts work with a shared modifier called "kitty_mod". The default is ctrl+shift but I felt that was a little hard to reach and remapped it to alt+shift. 

Some useful configs:

```text
inactive_text_alpha -0.6
# fade text for inactive windows (focus indicator)
```

### Cheat sheet - some of the most useful shortcuts

`kitty_mod+Z` = Zoom
`Cmd+Enter` or `kitty_mod+Enter`: new kitty window (= new pane within the current tab). This will place automatically in function of the selected [layout](https://sw.kovidgoyal.net/kitty/overview/#layouts).
Remap the command to `new_window_with_cwd` to have it open at the current working dir.
`kitty_mod+[ or ]`: previous / next window
`Cmd+t or kitty_mod+T`: new tab
`Shift+Cmd+[ or ]`: previous / next tab
`kitty_mod+H` = edit scrollback in nvim (there is a sample configuration line to uncomment for that). The `q` key is remapped to exit.
`kitty_mod+L` = switch layout... there are 7 of them. You can configure which ones are enabled—more on that below.
`kitty_mod+P,F` = pick a file, insert in terminal (this is one of several uses of the “hint kitten”, more on that below)
`kitty_mod+F3` = command palette

## Layouts

Something I used a lot in I3. Instead of deciding whether you want to split a window to the right or the bottom, the layout decides that for you. There are 7 layout total. I just kept 4:

- Fat (large window at top, split vertically at bottom)
- Tall (large window on left, split horizontally on right)
- Grid
- Stack

The stack layout is very handy for zooming a single window, but I mapped that one separately to `Mod+Z`.

## Kittens

Extensibility is the strong point of Kitty, I feel, when comparing with Ghostty. Ghostty has a very nice out of the box experience but still a little immature in terms of extensibility. This is done through ["kittens"](https://sw.kovidgoyal.net/kitty/kittens/). There are a number of super useful ones, out of the box.

### Choosing a font

Use `kitten choose-fonts` to pick a font. I tried a few, settled on [Victor Mono](https://rubjo.github.io/victor-mono/), downloaded with Homebrew:

```bash
brew install font-victor-mono
```

In some (most?) terminals you are advised to install a “nerd font”, which has some extra icons. But kitty will actually transparently detect these icons and render them so this is not necessary.

### Open anything

Kitten hints, this shows a letter or number by everything that looks like a file, so you can open it in your favorite editor, little like Vimium. I added a shortcut to open in nvim (mapping q to quit, like in the scrollback pager edit action):

```text
map --allow-fallback=shifted,ascii kitty_mod+p>e kitten hints --type path --program="launch --type=overlay nvim --cmd 'nnoremap q ZQ'"
```

This is a really awesome feature for the mouse-adverse crowd.

### Notifications

Another seemingly minor but very useful feature, "kitten notify" replaces `terminal-notifier` but is smarter about
knowing which kitty window triggered the notification.  I use this as completion hook for my coding agent.

## Final (first) impression

After a weekend of use, performance is good, I'm getting more and more used to the different shortcuts and way of
working things, and keep finding little gems.  I've only scratched the surface - I'll keep updating this as I find more
of them!

