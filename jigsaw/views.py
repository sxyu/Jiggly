from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django_ajax.decorators import ajax
import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import Game, Round, Player, Word, GameInstance, RoundReport
from easy_pdf.views import PDFTemplateView
from django.utils import translation

def _setCookie(response, key, value, days_expire = 9999):
  if days_expire is None:
    max_age = 365 * 24 * 60 * 60  #one year
  else:
    max_age = days_expire * 24 * 60 * 60 
  expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
  response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)

def _autoDelSession(request, response):
    if request.GET and 'clear' in request.GET:
        try:
            pid = request.COOKIES.get('psessionid') 
            _setCookie(response, 'psessionid', '')
            if pid and pid >= 0:
                player = Player.objects.get(pk=pid)
                g = player.instance
                if g.system:
                    g.delete()
                    player.delete()
                    _setCookie(response, 'instanceid', '')
            return response
        except:
            _setCookie(response, 'psessionid', '')
            return response
    else:
        pid = request.COOKIES.get('psessionid') 
        if pid == "0":
            return HttpResponseRedirect(reverse('scoreboard'))
        elif pid:
            return HttpResponseRedirect(reverse('play'))
        else:
            return response

def _curGame(request):
    try:
        gid = request.COOKIES.get('gameid') 
        if gid:
                return get_object_or_404(Game, key=gid)
    except:
        pass

def _recentGames(request):
    try:
        glist = request.COOKIES.get('recentgames') 
        if glist:
            ret = []
            for gid in glist.split('\\'):
                ret += [get_object_or_404(Game, key=gid)]
            return ret
    except:
        pass
def index(request):
    return _autoDelSession(request, render(request, 'jigsaw/index.html', {'p_home':True,'game':_curGame(request), 'recent': _recentGames(request)}))

def help(request):
    return _autoDelSession(request, render(request, 'jigsaw/help.html', {'p_help':True,'game':_curGame(request), 'recent': _recentGames(request)}))

def start(request):
    try:
        public = 'public' in request.GET and request.GET['public'] == 'true'
        if 'game' in request.GET and request.GET['game']:
            game = Game.objects.get(key=request.GET['game'])
        else:
            game = _curGame(request)
        return _autoDelSession(request, render(request, 'jigsaw/create.html', {'p_newgame':True,'public':public,'game':_curGame(request), 'base':game, 'recent': _recentGames(request)}))
    except:
        raise Http404

def join(request):
    return _autoDelSession(request, render(request, 'jigsaw/join.html', {'p_join':True,'game':_curGame(request), 'recent': _recentGames(request), 'games':GameInstance.objects.filter(public=True).filter(ended=False)}))

def newGame(request):
    g = Game.objects.create(name=_("My Game"), creator=_("Anonymous"))
    r = g.rounds.create(order=1, name=_("New Round"))
    return _autoDelSession(request, HttpResponseRedirect(reverse('game', args=[g.key])))

def game(request, id):
    g = get_object_or_404(Game, key=id)
    glist = request.COOKIES.get('recentgames')
    nglist = []
    if glist:
        glist = glist.split('\\')
        for x in glist:
            if x != id:
                nglist += [x]
    cg = request.COOKIES.get('gameid') 
    if cg and cg >= 0 and Game.objects.filter(key=cg).exists() and not cg == g.key:
        nglist += [cg]
    g.normalizeOrder()
    g.deleteStaleInstances()
    if g.instances.all().count():
        started = True
    else:
        started = False
    if len(nglist) and not cg == g.key:
        r = render(request, 'jigsaw/game.html', {'p_newgame':True, 'game':g, 'recent': [Game.objects.get(key=x) for x in nglist], 'started': started})
        _setCookie(r, 'recentgames', "\\".join(nglist))
    else:
        r = render(request, 'jigsaw/game.html', {'p_newgame':True, 'game':g, 'recent': _recentGames(request), 'started':started})
    _setCookie(r, 'gameid', g.key)
    return _autoDelSession(request, r)

def scoreboard(request):
    pid = request.COOKIES.get('psessionid') 
    if not pid and pid != 0:
        raise Http404
    if pid == '0':
        gid = request.COOKIES.get('instanceid') 
        key = request.COOKIES.get('instancemankey') 
        try:
            gm = Game.objects.get(key=key)
        except:
            return HttpResponseRedirect('/?clear=true')
        g = get_object_or_404(GameInstance, pk=gid)
        if gm != g.game:
            raise Http404
        return render(request, 'jigsaw/scoreboard.html', {'p_join':True, 'instance':g, 'game': gm, 'in_game':True, 'supervisor': True, 'scoreboard':True})
    else:
        try:
            player = Player.objects.get(pk=pid)
        except:
            return HttpResponseRedirect('/?clear=true')
        g = player.instance
        r = render(request, 'jigsaw/scoreboard.html', {'p_join':True, 'instance':g, 'session': player, 'round':player.round, 'game':g.game, 'in_game':True, 'scoreboard':True})
        _setCookie(r, 'instanceid', g.id)
        return r

def report(request):
    gid = request.COOKIES.get('instanceid') 
    pid = request.COOKIES.get('psessionid') 
    if not pid and pid != 0:
        raise Http404
    if pid == '0':
        key = request.COOKIES.get('instancemankey') 
        gm = get_object_or_404(Game, key=key)
        g = get_object_or_404(GameInstance, pk=gid)
        if gm != g.game:
            raise Http404
        return render(request, 'jigsaw/report.html', {'p_join':True, 'instance':g, 'rounds':g.game.rounds.all(), 'game': g.game, 'in_game':True, 'supervisor': True, 'scoreboard':True})
    else:
        return HttpResponseRedirect(reverse('scoreboard'))

class reportPDF(PDFTemplateView):
    template_name = "jigsaw/reportpdf.html"
    
    def get_context_data(self, **kwargs):
        gid = self.request.COOKIES.get('instanceid') 
        pid = self.request.COOKIES.get('psessionid') 
        if not pid and pid != 0:
            raise Http404
        if pid == '0':
            key = self.request.COOKIES.get('instancemankey') 
            gm = get_object_or_404(Game, key=key)
            g = get_object_or_404(GameInstance, pk=gid)
            if gm != g.game:
                raise Http404
            context =  super(reportPDF, self).get_context_data(
                pagesize="Letter",
                title=_('Jiggly Game Report: ') + g.alias, **kwargs)
            context['p_join'] = True;
            context['instance'] = g;
            context['rounds'] = g.game.rounds.all();
            context['game'] = g.game;
            context['in_game'] = True;
            context['supervisor'] = True;
            return context
        else:
            raise Http404

def play(request):
    pid = request.COOKIES.get('psessionid') 
    if pid and pid >= 0:
        try:
            player = Player.objects.get(pk=pid)
        except:
            return HttpResponseRedirect('/?clear=true')
        if player.round is None:
            return HttpResponseRedirect(reverse('scoreboard'))
        else:
            if player.round.type:
                type = player.round.getTypeAlias()
                return render(request, 'jigsaw/play_%s.html' % type, {'p_join':True, 'game':player.round.game, 'round':player.round, 'player':player,'instance':player.instance, 'in_game':True, 'type':type})
            else:
                return render(request, 'jigsaw/play_jigsaw.html', {'p_join':True, 'game':player.round.game, 'round':player.round, 'player':player,'instance':player.instance, 'in_game':True, 'type':'jigsaw'})
    else:
        raise Http404

def printDoc(request, gid, id):
    g = get_object_or_404(Game, key=gid)
    r = get_object_or_404(Round, pk=id)
    if r.game == g:
        return _autoDelSession(request, render(request, 'jigsaw/print.html', {'p_newgame':True, 'game':g, 'round':r}))
    else:
        raise Http404

def changeLang(request):
    if request.method == "GET":
        if 'code' in request.GET:
            id = request.GET['code']
            if 'redir' in request.GET:
                r =  HttpResponseRedirect(request.GET['redir'])
            if id:
                if hasattr(request, 'session'):
                    request.session['django_language'] = id
                _setCookie(r, settings.LANGUAGE_COOKIE_NAME, id)
                translation.activate(id)
            return r

@csrf_exempt
@ajax
def getWords(request):
    try:
        if request.method == "GET":
            id = request.GET['id']
            r = get_object_or_404(Round, pk=id)
            words = []
            words += r.words.all()
            from random import shuffle, seed, randint
            seed()
            shuffle(words)
            t = []
            for w in words:
                r = randint(0,1)
                if r:
                    t += [w.word, w.meaning, str(w.pk), '1']
                else:
                    t += [w.meaning, w.word, str(w.pk), '0']
            return '\n'.join(t)
    except Exception, ex:
        return str(ex)

@csrf_exempt
@ajax
def getWordsUnmatched(request):
    if request.method == "GET":
        id = request.GET['id']
        r = get_object_or_404(Round, pk=id)
        words = []
        words += r.words.all()
        from random import shuffle, seed, randint
        seed()
        shuffle(words)
        t = []
        df = [x.meaning for x in words]
        for w in words:
            t += [w.word, str(w.pk)]
        
        for i in range(2):
            for d in range(0,len(df)-1,2):
                rd = randint(0,1);
                if rd:
                    df[d], df[d+1] = df[d+1], df[d]
            for d in range(1,len(df)-1,2):
                rd = randint(0,1);
                if rd:
                    df[d], df[d+1] = df[d+1], df[d]
        t += df
        return '\n'.join(t)

@csrf_exempt
@ajax
def gradeRound(request):
    if request.method == "GET":
        id = request.GET['id']
        r = get_object_or_404(Round, pk=id)
        state = request.GET['state'].split('\n')
        
        # initialize variables
        pts = 0
        wordct = 0
        t = {}
        maxscore = 0

        # grade the words
        for w in r.words.all():
            t[w.id] = 0
            maxscore += w.points
        for s in state:
            if not s:
                continue
            wordstate = s.split('\\')
            word = get_object_or_404(Word, pk=wordstate[0])
            if word.meaning == wordstate[1]:
                pts += word.points
                t[word.id] = 1;
                wordct += 1

        totalw = len(r.words.all())

        if wordct == totalw: 
            pts += r.points
            rb = True
        else:
            rb = False
        maxscore += r.points

        good = []
        words = []
        correct = []

        for w, v in t.iteritems():
            word = get_object_or_404(Word, pk=w)
            if v:
                correct += [word.word,] 
            words += [word,] 
            good += [v,]

        pid = request.COOKIES.get('psessionid') 
        if pid and pid >= 0:
            player = get_object_or_404(Player, pk=pid)
            RoundReport.objects.create(round=player.round, player=player, instance=player.instance, 
                                       points=pts, totalpoints=pts+player.points, roundbonus=rb, wordscorrect='\n'.join(correct))
            player.round = player.round.next()
            player.points += pts
            player.save()
            return render(request, 'jigsaw/round_end.html', {'score':pts, 'session': player, 'instance':player.instance, 'max_score': maxscore, 'round':r, 'game':r.game, 'words':zip(words, good), 'round_bonus':rb})
        else:
            return render(request, 'jigsaw/round_end.html', {'score':pts, 'max_score': maxscore, 'instance':player.instance, 'round':r, 'game':r.game, 'words':zip(words, good), 'round_bonus':rb})
@ajax
@csrf_exempt
def delGame(request):
    if request.method == "POST":
        id = request.POST['id']
        g = get_object_or_404(Game, key=id)
        g.delete()

@ajax
@csrf_exempt
def modGameName(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            g = get_object_or_404(Game, key=id)
            name = request.POST['content'].replace('\\', '')
            g.name = name
            g.save()
    except:
        return "Failed"

@ajax
@csrf_exempt
def modGameCreator(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            g = get_object_or_404(Game, key=id)
            name = request.POST['content'].replace("\\", "")
            g.creator = name
            g.save()
    except:
        return "Failed"

@ajax
@csrf_exempt
def modGameAddRound(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            g = get_object_or_404(Game, key=id)
            r = g.rounds.create(order=g.last, name=_("New Round"), type='J')
            g.last += 1
            g.save()
            return render(request, 'jigsaw/round.html', {'round':r, 'game':g})
    except:
        return "Failed"

@ajax
@csrf_exempt
def modRoundName(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            r = get_object_or_404(Round, pk=id)
            modkey = request.POST['key']
            if modkey != r.game.key:
                return HttpResponseForbidden("403")
            name = request.POST['content'].replace("\\", "")
            r.name = name
            r.save()
    except:
        return "Failed"

@ajax
@csrf_exempt
def modRoundPoints(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            r = get_object_or_404(Round, pk=id)
            modkey = request.POST['key']
            if modkey != r.game.key:
                return HttpResponseForbidden("403")
            bonus = request.POST['content']
            r.points = bonus
            r.save()
    except:
        return "Failed"

@ajax
@csrf_exempt
def modRoundType(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            r = get_object_or_404(Round, pk=id)
            modkey = request.POST['key']
            if modkey != r.game.key:
                return HttpResponseForbidden("403")
            type_name = request.POST['content']
            r.type = type_name
            r.save()
            return r.getType()
    except:
        return "Failed"

@ajax
@csrf_exempt
def modRoundAddWord(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            r = get_object_or_404(Round, pk=id)
            if len(r.words.all()) >= 31:
                return ""
            modkey = request.POST['key']
            if modkey != r.game.key:
                return HttpResponseForbidden("403")
            w = r.words.create(word=_('New Word'),meaning=_('Enter Definition Here'))
            return render(request, 'jigsaw/word.html', {'word':w, 'round':r})
    except:
        return "Failed"

@ajax
@csrf_exempt
def delRound(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            r = get_object_or_404(Round, pk=id)
            modkey = request.POST['key']
            if modkey != r.game.key:
                return HttpResponseForbidden("403")
            r.delete()
    except:
        pass

@ajax
@csrf_exempt
def modWord(request):
    if request.method == "POST":
        try:
            id = request.POST['id']
            w = get_object_or_404(Word, pk=id)
            modkey = request.POST['key']
            if modkey != w.round.game.key:
                return HttpResponseForbidden("403")
            if 'word' in request.POST and request.POST['word']:
                w.word = request.POST['word'].replace("\\", "")
            if 'meaning' in request.POST and request.POST['meaning']:
                w.meaning = request.POST['meaning'].replace("\\", "")
            if 'points' in request.POST and request.POST['points']:
                w.points = request.POST['points']
            w.save()
        except:
            pass

@ajax
@csrf_exempt
def delWord(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            w = get_object_or_404(Word, pk=id)
            modkey = request.POST['key']
            if modkey != w.round.game.key:
                return HttpResponseForbidden("403 Forbidden")
            w.delete()
    except:
        pass

@ajax
@csrf_exempt
def moveRound(request):
    try:
        if request.method == "POST":
            id = request.POST['id']
            r = get_object_or_404(Round, pk=id)
            modkey = request.POST['key']
            if modkey != r.game.key:
                return HttpResponseForbidden("403 Forbidden")
            found = False  
            down = ('down' in request.POST and request.POST['down'] == 'true')
            if down:
                cur = r.order+1
            else:
                cur = r.order-1
            while not found:
                try:
                    other = r.game.rounds.get(order=cur)
                    found = True
                except:
                    if down:
                        cur += 1
                    else:
                        cur -= 1
                    if cur <= 0 or cur >= r.game.last:
                        return "Failed"
            r.order = other.order
            if down:
                other.order = cur-1
            else:
                other.order = cur+1
            r.save()
            other.save()
            return "OK"
    except:
        return "Failed"
    
@ajax
@csrf_exempt
def createInstance(request):
    if request.method == "POST":
        id = request.POST['id']
        g = get_object_or_404(Game, pk=id)
        g.normalizeOrder()
        alias = request.POST['alias']
        host = request.POST['host']
        public = request.POST['public'] == 'true'
        totaltime = request.POST['totaltime']
        system = (('system' in request.POST) and request.POST['system'] == 'true')
        gi = GameInstance.objects.create(game=g, alias=alias, host=host, public=public, totaltime=totaltime, system=system)
        gi.save()
        return gi.pk

@ajax
@csrf_exempt
def endInstance(request):
    if request.method == "POST":
        id = request.POST['id']
        g = get_object_or_404(GameInstance, pk=id)
        
        key = request.COOKIES.get('instancemankey') 
        gm = get_object_or_404(Game, key=key)
        if gm != g.game:
            raise Http404

        g.delete()

@csrf_exempt
@ajax
def startSession(request):
    try:
        if request.method == "POST":
            if 'id' in request.POST:
                id = request.POST['id']
                g = GameInstance.objects.get(pk=id, ended=False)
            else:
                alias = request.POST['alias']
                g = GameInstance.objects.get(alias__iexact=alias, ended=False)
            round = g.game.first()
            name = request.POST['name']
            if not name:
                return ''
            p = Player.objects.create(instance=g, name=name, round=round)
            return p.pk
    except:
        return ''

@ajax
@csrf_exempt
def aliasExists(request):
    if request.method == "GET":
        if GameInstance.objects.filter(alias__iexact=request.GET['alias'], ended=False).exists():
            return 1
        else:
            return 0

@ajax
@csrf_exempt
def checkGameEnded(request):
    if request.method == "GET":
		if not GameInstance.objects.filter(id=request.GET['id']).exists():
			return 2
		elif GameInstance.objects.get(id=request.GET['id']).ended:
			return 1
		else:
			return 0

@ajax
@csrf_exempt
def endGame(request):
    if request.method == "POST":
        g = GameInstance.objects.get(id=request.POST['id'])
        g.ended = True
        g.save()

@ajax
@csrf_exempt
def updateScoreboard(request):
    gid = request.COOKIES.get('instanceid')
    gi = GameInstance.objects.get(pk=gid)
    return render(request, "jigsaw/scoreboard_update.html", context={'instance':gi, 'game':gi.game})

@ajax
@csrf_exempt
def updateJoin(request):
    return render(request, "jigsaw/join_update.html",
        context={'games':GameInstance.objects.filter(public=True, ended=False)})
