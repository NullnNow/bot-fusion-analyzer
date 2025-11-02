# Fusion Analyzer

Discord bot, provides feedback on custom sprites for the game [Pokémon Infinite Fusion](https://infinitefusion.fandom.com/wiki/Pok%C3%A9mon_Infinite_Fusion_Wiki).

# Credits

- **Aegide** as the original creator of the Fusion Bot
- **Doodledoo** is the creator of this fork and added features
- **Greystorm** for giving permission to use various utilities from spritebot

# Changelog
## Version 2.5
- **Ping analysis:** if you simply ping the bot, it will analyze any sprites attached to that message
- If the filename is correct, it will now show the letter (if there's any) in the title. For instance, **Valid: 1.1b**
- The analysis embed now looks slightly different in order to allow for more dynamic stuff in the future
- Automatic analysis will not happen if the post has certain tags, to avoid unwanted analysis on Non-IF or trainer cards
- Some big internal changes to organize the current modules in distinct packages
- Fix: archived threads weren't being fetched properly in spriter applications
- Fix: ignore attachments that aren't images

## Version 2.4
- **Intentional transparency**: by adding this keyword to gallery posts, Fusion Bot won't reject a sprite that has semi transparent pixels
- Support for the new egg sprite filename format (it's now 123_egg.png)
- Tutorial Mode improvements and new sections
- Basic AI detection and warnings

## Version 2.3
- **Automatic analysis in #spritework.** There's an option to opt out of it.
- **Tutorial Mode** with some information on Fusion Bot messages! Non-spriters will get a prompt for it with their automatic analysis. Other way to use it is through the /help command.
- More understandable issues for certain issues such as half pixels and semi transparency
- Fix: pixels with "color" but full transparency now won't count towards half pixels
- Fix: Necrozma body autogens are now hidden as it turns out the sheets show Ultra Necrozma instead

## Version 2.2
- **Autogens are back!** Analyzed fusions will have the corresponding autogen sprite in the analysis embed
- **Triple** fusion and **Egg** sprite support
- Detect other image formats "disguised" as PNGs

## Version 2.1
- New Hoenn dex numbers
- **Spriter application checks:** it will do an auto-analysis of the 3 sprites and check if their spritework threads have been created over a day ago
- **Misnumbered IDs:** when a gallery posts has a misnumbered ID between message and filename, the gallery message will be deleted and sent to the user to be able to fix and repost it
- **Zigzag** posts in the galleries will now be analyzed
- It will now detect when there's no half pixels but it doesn't adhere to the grid

## Version 2.0
- **Similarity score** now works with **indexed mode** sprites (previously it was always 0)
- **Pokemon names** are now displayed when the dex IDs are valid
- **Similar command**: it will return a text list with at most 20 pairs of similar colors that could be merged into a single shade.
- **Assets gallery support** for custom bases, which will also display their pokemon name in the analysis.
- **High similarity warnings** and different similarity and color count restrictions, depending on if it's a fusion or custom base.
- Fix: the bot won't flip out when a single message has multiple different fusion with their IDs in the message
