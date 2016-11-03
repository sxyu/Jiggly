from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import os, uuid
from binascii import hexlify

def _createId():
    return hexlify(os.urandom(16))

class Game(models.Model):
    key = models.CharField(max_length=32, default=_createId)
    name = models.CharField(max_length=100)
    creator = models.CharField(max_length=150)
    time = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    last = models.IntegerField(default=2)
    def __str__(self):
        return self.name.encode('utf-8')
    class Meta:
        ordering = ['-time']
    def first(self):
        try:
            return self.rounds.all()[0]
        except:
            return None
    def normalizeOrder(self):
        i = 1
        cur = self.first()
        while cur:
            if cur.order != i:
                cur.order = i
                cur.save()
            cur = cur.next()
            i += 1
        self.last = i
        self.save()
    def deleteStaleInstances(self):
		for i in self.instances.all():
			if i.players.all().count() == 0:	
				i.delete()
    def defaultAlias(self):
        return self.name.replace(' ','').replace('_','').replace('-','').lower()[:20]
    def maxPoints(self):
        total = 0
        for r in self.rounds.all():
            total += r.maxPoints()
        return total

class Round(models.Model):
	game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rounds")
	name = models.CharField(max_length=100, blank=True)
	TYPE_CHOICES = (
			("J", _("Jigsaw")),
			("M", _("Matching"))
	)
	TYPE_CHOICES_ALIAS = (
			("J", "jigsaw"),
			("M", "matching")
	)
	type = models.CharField(choices=TYPE_CHOICES, max_length=1, blank=True)
	order = models.IntegerField(editable=False)
	points = models.IntegerField(default=100)
	def __str__(self):
		return "%s - #%s: %s" % (str(self.game), str(self.order), self.name.encode('utf-8'))
	class Meta:
		ordering = ['order']
	def next(self):
		r = self.order + 1;
		nxt = None 
		while not nxt and r < self.game.last:
			try:
				nxt = self.game.rounds.get(order=r)
			except:
				r += 1
		return nxt
	def maxPoints(self):
		total = 0
		for w in self.words.all():
			total += w.points
		total += self.points
		return total
	def completeCount(self):
		return self.order - 1
	def getType(self):
		if self.type:
			return self.get_type_display() 
		else:
			return _('Jigsaw'); 
	def getTypeAlias(self):
		if self.type:
			return dict(self.TYPE_CHOICES_ALIAS)[self.type]
		else:
			return _('jigsaw'); 

class Word(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name="words")
    word = models.CharField(max_length=150)
    meaning = models.CharField(max_length=250)
    points = models.IntegerField(default=50)
    def __str__(self):
        return "%s : %s" % (self.word.encode('utf-8'), self.meaning.encode('utf-8'))
    class Meta:
        ordering = ['word']
 
class GameInstance(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="instances")
    alias = models.CharField(max_length=90)
    host = models.CharField(max_length=150, blank=True)
    public = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
    totaltime = models.IntegerField(default=1800)
    passedtime = models.IntegerField(default=0, editable=False)
    system = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    class Meta:
        ordering = ['-time']
    def __str__(self):
        return "%s: %s" % (str(self.game), str(self.pk))
    def maxPoints(self):
        return self.game.maxPoints()
    def averagePoints(self):
        total = 0
        ct = 0
        for p in self.players.all():
            total += p.points
            ct += 1
        if ct == 0:
            return "-"
        return total/ct
    
class Player(models.Model):
    instance = models.ForeignKey(GameInstance, on_delete=models.CASCADE, related_name="players")
    round = models.ForeignKey(Round, on_delete=models.SET_NULL, null=True, editable=False, related_name="players")
    name = models.CharField(max_length=100)
    points = models.IntegerField(default=0, editable=False)
    time = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    class Meta:
        ordering = ['-points']
    def rank(self):
        return self.instance.players.filter(points__gt=self.points).count() + 1
    
class RoundReport(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, editable=False, related_name="reports")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, editable=False, related_name="reports")
    instance = models.ForeignKey(GameInstance, on_delete=models.CASCADE, editable=False, related_name="reports")
    points = models.IntegerField(default=0, editable=False)
    totalpoints = models.IntegerField(default=0, editable=False)
    wordscorrect = models.TextField(blank=True, editable=False)
    roundbonus = models.BooleanField(default=False, editable=False)
    boardinfo = models.TextField(blank=True, editable=False)
    def averagePoints(self):
        total = 0
        ct = 0
        for p in self.instance.reports.filter(round=self.round):
            total += p.points
            ct += 1
        if ct == 0:
            return "-"
        return total/ct
    def maxPoints(self):
        return self.round.maxPoints()
    def wordCorrect(self, word):
        return word in self.wordscorrect.split('\n')
