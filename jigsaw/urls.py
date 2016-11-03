from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^help/$', views.help, name='help'),
    url(r'^new/$', views.newGame, name='new_game'),
    url(r'^scores/$', views.scoreboard, name='scoreboard'),
    url(r'^start/$', views.start, name='start'),
    url(r'^join/$', views.join, name='join'),
    url(r'^report/$', views.report, name='report'),
    url(r'^report/export/$', views.reportPDF.as_view(), name='report_pdf'),
    url(r'^game/(?P<id>.+)/$', views.game, name='game'),
    url(r'^print/(?P<gid>.+)-(?P<id>.+)/$', views.printDoc, name='print'),
    url(r'^play/$', views.play, name='play'),
    url(r'^redir/(?P<url>.+)/$', views.redir, name='redir'),
    url(r'^language/$', views.changeLang, name='change_lang'),

    url(r'^ajax_gamedel/$', views.delGame, name='del_game'),
    url(r'^ajax_gamemod_name/$', views.modGameName, name='mod_game_name'),
    url(r'^ajax_gamemod_creator/$', views.modGameCreator, name='mod_game_creator'),
    url(r'^ajax_gamemod_roundadd/$', views.modGameAddRound, name='mod_game_add_round'),

    url(r'^ajax_rounddel/$', views.delRound, name='del_round'),
    url(r'^ajax_roundmod_name/$', views.modRoundName, name='mod_round_name'),
    url(r'^ajax_roundmod_points/$', views.modRoundPoints, name='mod_round_points'),
    url(r'^ajax_roundmod_type/$', views.modRoundType, name='mod_round_type'),
    url(r'^ajax_roundmod_wordadd/$', views.modRoundAddWord, name='mod_round_add_word'),
    url(r'^ajax_roundmove/$', views.moveRound, name='move_round'),

    url(r'^ajax_worddel/$', views.delWord, name='del_word'),
    url(r'^ajax_wordmod/$', views.modWord, name='mod_word'),

    url(r'^ajax_getwords/$', views.getWords, name='get_words'),
    url(r'^ajax_getwords_unmatched/$', views.getWordsUnmatched, name='get_words_unmatched'),
    url(r'^ajax_roundgrade/$', views.gradeRound, name='grade_round'),

    url(r'^ajax_startsession/$', views.startSession, name='start_session'),
    url(r'^ajax_createinstance/$', views.createInstance, name='create_instance'),
    url(r'^ajax_endinstance/$', views.endGame, name='end_game'),
    url(r'^ajax_delinstance/$', views.endInstance, name='del_instance'),
    url(r'^ajax_checkgameended/$', views.checkGameEnded, name='del_instance'),

    url(r'^ajax_aliasexists/$', views.aliasExists, name='alias_exists'),
    url(r'^ajax_updatescoreboard/$', views.updateScoreboard, name='update_scoreboard'),
    url(r'^ajax_updatejoin/$', views.updateJoin, name='update_join'),
]
