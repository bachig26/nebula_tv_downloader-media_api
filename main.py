import logging
from config.Config import Config
from NebulaAPI.Authorization import NebulaUserAuthorzation
from NebulaAPI.VideoFeedFetcher import get_all_channels_slugs_from_video_feed
from NebulaAPI.ChannelVideos import get_channel_video_content
from utils.MetadataFilesManager import (
    create_channel_subdirectory_and_store_metadata_information,
)
from utils.Filtering import filter_out_episodes


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

CONFIG = Config()

NEBULA_AUTH = NebulaUserAuthorzation(
    userToken=CONFIG.NebulaAPI.USER_API_TOKEN,
    authorizationHeader=CONFIG.NebulaAPI.AUTHORIZATION_HEADER,
)


def main() -> None:
    if CONFIG.NebulaFilters.CHANNELS_TO_PARSE:
        channels = CONFIG.NebulaFilters.CHANNELS_TO_PARSE
        logging.debug("Using channels from config: %s", channels)
    else:
        channels = get_all_channels_slugs_from_video_feed(
            authorizationHeader=NEBULA_AUTH.get_authorization_header(full=True),
            categoryFeedSelector=CONFIG.NebulaFilters.CATEGORY_SEARCH,
            cursorTimesLimitFetchMaximum=1,
        )
    for channel in channels:
        logging.info("Fetching episodes for channel `%s`", channel)
        channelData = get_channel_video_content(
            channelSlug=channel,
            authorizationHeader=NEBULA_AUTH.get_authorization_header(full=True),
        )
        logging.info(
            "Found %s episodes for channel `%s`",
            len(channelData.episodes.results),
            channel,
        )
        filteredEpisodes = list(
            filter_out_episodes(
                filterSettings=CONFIG.NebulaFilters,
                episodes=channelData.episodes.results,
            )
        )
        logging.info("Filtered down to %s episodes", len(filteredEpisodes))
        create_channel_subdirectory_and_store_metadata_information(
            channelSlug=channel,
            channelData=channelData.details,
            episodesData=channelData.episodes,
            outputDirectory=CONFIG.Downloader.DOWNLOAD_PATH,
        )
        for episode in filteredEpisodes:
            logging.info(
                "Downloading episode `%s` from channel `%s`",
                episode.slug,
                channel,
            )
    return


if __name__ == "__main__":
    main()
