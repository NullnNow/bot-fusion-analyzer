from bot.core.analysis import Analysis


async def main(analysis_list: list[Analysis]):
    """Does some checks from content_analysis with harsher restrictions and some entirely different checks"""
    if (not analysis_list) or (len(analysis_list) == 0):
        return

    # WHAT IT'S GOING TO DO:
    # Grab filename of the first image. Extract ID, compare with the message ID, compare all other images too.
        # If it doesn't match, issue. If the message has no ID, issue.
            # Separate the gallery misnumbered behavior into the new analyzer methods.
            # Have a boolean to mark if there's a misnumbered issue so that it doesn't use has_issue()
            # This means that the actual issue isn't needed in the gallery, only the boolean
            # Edit the message to show Pokémon names of the filename and content IDs in the warning message
        # For any of the other images, issue if the ID doesn't match the first one
    # Correct gallery checks
        # If it's sprite gallery, ensure it's only a fusion or triple fusion
        # If it's assets gallery, ensure it's only a base or egg
    # If all the filenames match, text checker (beta version that only mentions it in the analysis)
        # Either grab the full names of each Pokémon or a minimal version that allows for misspellings
        # Ensure both names exist in the gallery message. If they don't, have a new easily searchable issue
        # After a trial period it can be determined if the name checker is too strict, how often do misspellings
        # happen, how flexible it is, and if it actually enforces cases where the names don't match
    # Letter checks
        # Month search:
            # Search for previous gallery post within the same month by that user
            # If one matches the current message, ensure that none of its images have the same filename as any of
            # the current images. Issue if it does.
            # If there are n images in a previous matching post, take it into account for the next part
        # Ensure that the new sprites have letters that start at N previous images and continue the pattern for M
        # 1 nothing, 2a, 3b, 4c, 5d, number being N + M
        # Since the order cannot be guaranteed, have a boolean array of M size that goes from letter N to N+M
        # If any attachment has a letter higher than N + M, put an issue on that analysis
        # At the end, if any letter is unfilled, put an issue in the first analysis


    # Move NANI and ping behavior to gallery specific methods in analyzer

    await same_id_checks(analysis_list)
    await correct_gallery_checks()
    await pokemon_name_checks()
    await filename_letter_checks()


async def same_id_checks(analysis_list: list[Analysis]):
    first_analysis = analysis_list[0]
    filename_fusion_id, id_type = first_analysis.generate_fusion_filename()

    for analysis in analysis_list:
        analysis_filename_id, analysis_id_type = analysis.generate_fusion_filename()


async def correct_gallery_checks():
    pass


async def pokemon_name_checks():
    pass


async def filename_letter_checks():
    pass