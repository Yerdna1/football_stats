# callbacks/__init__.py
from .winless_streaks_callback import setup_winless_streaks_callbacks
from .team_analysis_callback import setup_team_analysis_callbacks
from .next_fixtures_callback import setup_next_fixtures_callbacks
from .league_stats_callback import setup_league_stats_callbacks
from .form_analysis_callback import setup_form_analysis_callbacks

# Call the setup functions with the required arguments in your app setup
def setup_callbacks(app, api):
    setup_winless_streaks_callbacks(app, api)
    setup_team_analysis_callbacks(app, api)
    setup_next_fixtures_callbacks(app, api)
    setup_league_stats_callbacks(app, api)
    setup_form_analysis_callbacks(app, api)
