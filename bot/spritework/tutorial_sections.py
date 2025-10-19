class TutorialSection:
    title: str
    description: str
    content: str
    image: str

    def __init__(self, title, description, content, image: str|None = None):
        self.title = title
        self.description = description
        self.content = content
        self.image = image


filename = TutorialSection(
    title="Filename",
    description="What should my filename be? What's the correct format?",
    content="With fusion sprites, your filename should be 2 numbers, with a dot in between.\n"
            "For instance: **102.463.png** (most likely, your program will add the png part on its own)\n"
            "The numbers represent the pokedex numbers of the pokemon in your fusion. "
            "**Warning:** Infinite Fusion uses different pokedex numbers, so don't take them from the main games! "
            "Instead, use the **dex command** to know the filenames. For example, write: `dex Ludicolo/Probopass` "
            "in a message, and you will trigger the command.\n"
            "For triple fusions, it'd be 3 numbers, and for custom bases, only one.\n"
            "**For more info:** https://discord.com/channels/302153478556352513/873571372981452830/909609434316177419",
    image="filenames.png"
)

colors = TutorialSection(
    title="Color count",
    description="What's the color count? How many colors can I use?",
    content="In pixel art, and particularly here, the amount of colors used in a sprite matters. Pokemon sprites "
            "were limited to 16 but we use more.\nIf it's for a fusion, try to keep it below 32. Make each color "
            "count and try to re-use colors whenever possible.\n"
            "For more information, check out the relevant part of the Spriting Guidelines: "
            "https://discord.com/channels/302153478556352513/873571372981452830/909615749411270676"
)

similarity = TutorialSection(
    title="Similarity score",
    description="What does it mean? How much is too much similarity?",
    content="A common misconception is that it's measuring how similar your sprite is to something else. Far from it!\n"
            "It's grabbing the colors you used on your sprite, and comparing them against eachother. This is to ensure "
            "that your colors are distinct enough.\nIf it's for a fusion, try to keep your similarity to 7 or below. "
            "Anything over 10 most of the time means that you have some unaccounted colors in there that are *almost "
            "identical* to others you used, yet not quite the same shade.\nWrite ?tag analyser for a link to a website "
            "that will show you which color pairs are the most similar, so that you can convert them into a single "
            "color.\nYou can use the /similar command to check the color pairs too!"
)

grid = TutorialSection(
    title="Grid alignment",
    description="What does it mean if it says 'not aligned to the grid'?",
    content="If you see **not aligned to the grid** in a bot core, it means that after upscaling your sprite to "
            "288x288, you may have moved it in the canvas. But don't worry about this, as when the sprite is brought "
            "into the game, this misalignment will be automatically fixed.\n"
            "This warning on the bot is mostly so that people are aware of it."
)

size = TutorialSection(
    title="Sprite size",
    description="What's invalid size? Which size should I use?",
    content="Make sure you create sprites that are 96 pixels tall and wide. Then, you upscale them 300%. This lands "
            "it at a size of **288x288 pixels**. If you edit it after upscaling, you may run into **half pixels**.\n"
            "If you came across half pixels, check out that tutorial section too."
)

half_pixels = TutorialSection(
    title="Half pixels",
    description="What are half pixels? How do I detect them?",
    content="**Half pixels** occur when, for instance, one edits a sprite *after* they've upscaled them to 288x288. "
            "When you upscale a sprite, what was originally a pixel now becomes a square that's 3 pixels wide and "
            "tall. That means that the whole sprite should follow this pattern automatically. But if there's something "
            "that breaks that pattern, that's a half pixel. You can notice them if you zoom in and realize some spots "
            "look 'out of place'.\n"
            "In some cases, the *entire sprite* may be half pixels. This probably means that the sprite you had "
            "originally wasn't 96x96, so upscaling it made a bunch of half pixels appear. Try to recover the image "
            "before upscaling if you have it, and try upscaling with an external website. If you write `?tag upscaler` "
            "you will be linked to one of these.\n"
            "For more information, check out the relevant part of the Spriting Guidelines: "
            "https://discord.com/channels/302153478556352513/873571372981452830/909614622049460265",
    image="half_pixels.png"
)

transparency = TutorialSection(
    title="Semi transparent pixels",
    description="What is semi transparency and how can it be avoided?",
    content="If you see **semi transparent pixels** in the core, an additional embed will appear. They are "
            "highlighted in pink against the silhouette of your sprite. This kind of pixel is neither fully opaque "
            "or fully transparent, and may be caused by how certain programs upscale images. Another cause can be "
            "tools that are not at full transparency (such as a brush tool instead of using a pixel art pencil).\n"
            "Using semi transparent pixels *is* allowed if it's done intentionally though, such as for stuff like "
            "water bubbles or insect wings. The warning is there so that people are aware the sprite has them "
            "in case they're not intentional."
)

how_to_use = TutorialSection(
    title="How to use Fusion Bot",
    description="How can I make Fusion Bot analyze my sprite again?",
    content="If your sprite had some issues when you first posted it to spritework, don't worry! The spritework "
            "thread is where you can get feedback and improve on it to fix issues. If you want to check if the ones "
            "the bot detects have been fixed, **reply to your new image while pinging (using @) the Fusion Bot!**\n"
            "If you want to see how your sprite would look in the game (for instance, to check that it's correctly "
            "placed in the canvas) you can reply to the image writing `!battle` in your message."
)


sections = {
    "how_to_use": how_to_use,
    "filename" : filename,
    "colors" : colors,
    "similarity" : similarity,
    "half_pixels": half_pixels,
    "size": size,
    "transparency": transparency,
    "grid": grid
}

