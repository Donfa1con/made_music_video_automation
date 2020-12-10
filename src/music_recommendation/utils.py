import glob
import os
import random

GENRES = {
    'rock': {'abseiling', 'armwrestling', 'assemblingcomputer', 'benchpressing', 'carvingpumpkin', 'catchingfish',
             'changingoil', 'cleanandjerk', 'contactjuggling', 'cookingoncampfire', 'crossingriver', 'deadlifting',
             'digging', 'dodgeball', 'drinkingshots', 'exercisingarm', 'flyingkite', 'frontraises', 'gettingatattoo',
             'headbutting', 'highjump', 'highjump', 'iceclimbing', 'javelinthrow', 'paragliding', 'parasailing',
             'rockclimbing', 'sailing', 'singing', 'snatchweightlifting', 'squat', 'surfingcrowd'},

    'metal': {'airdrumming', 'archery', 'bendingmetal', 'bikingthroughsnow', 'bobsledding', 'choppingwood',
              'crackingneck', 'drinking', 'extinguishingfire', 'gymnasticstumbling', 'headbanging', 'hockeystop',
              'jugglingfire', 'kickingfieldgoal', 'kickingsoccerball', 'kitesurfing', 'motorcycling',
              'passingAmericanfootball(ingame)', 'playingbassguitar', 'playingdrums', 'playingicehockey',
              'playingpaintball', 'pumpingfist', 'ridingabike', 'ridingmountainbike', 'snowboarding', 'snowkiting',
              'swordfighting', 'tappingguitar', 'trapezing', 'wrestling'},

    'hiphop': {'breakdancing', 'bellydancing', 'bendingback', 'bowling', 'breakdancing', 'cheerleading',
               'dancinggangnamstyle', 'dribblingbasketball', 'dropkicking', 'drummingfingers', 'dunkingbasketball',
               'fingersnapping', 'hittingbaseball', 'hurdling', 'hurling(sport)', 'jogging', 'jugglingsoccerball',
               'jumpstyledancing', 'krumping', 'lunge', 'parkour', 'playingbasketball', 'pullups', 'punchingbag',
               'punchingperson(boxing)', 'pushup', 'ridingscooter', 'shakinghead', 'shootingbasketball',
               'skateboarding', 'skiingslalom', 'skippingrope', 'slapping', 'spraypainting', 'stretchingleg',
               'tapdancing', 'triplejump', 'zumba'},

    'jazz': {'blowingleaves', 'carryingbaby', 'celebrating', 'countingmoney', 'crying', 'decoratingthechristmastree',
             'foldingnapkins', 'jugglingballs', 'kissing', 'makingsnowman', 'openingpresent', 'playingcricket',
             'playingpiano', 'playingsaxophone', 'playingtrombone', 'playingtrumpet', 'presentingweatherforecast',
             'pushingwheelchair', 'readingbook', 'scubadiving', 'shovelingsnow', 'tobogganing', 'unboxing'},

    'disco': {'bellydancing', 'busking', 'cartwheeling', 'clapping', 'dancingcharleston', 'doingaerobics', 'yoga',
              'exercisingwithanexerciseball', 'gymnasticstumbling', 'hulahooping', 'playingvolleyball', 'tangodancing',
              'recordingmusic', 'robotdancing', 'salsadancing', 'stretchingarm', 'swingdancing', 'taichi'},

    'country': {'buildingcabinet', 'buildingshed', 'changingwheel', 'checkingtires', 'climbingtree',
                'countrylinedancing', 'cookingsausages', 'drinkingbeer', 'drivingtractor', 'icefishing', 'milkingcow',
                'playingpoker', 'ridingmechanicalbull', 'tastingbeer'},

    'classical': {'bakingcookies', 'blastingsand', 'blowingglass', 'bookbinding', 'dancingballet', 'divingcliff',
                  'drawing', 'faceplanting', 'feedingbirds', 'feedingfish', 'feedinggoats', 'givingorreceivingaward',
                  'playingcello', 'playingchess', 'playingclarinet', 'playingcymbals', 'playingharp', 'playingkeyboard',
                  'playingorgan', 'playingrecorder', 'playingviolin', 'ridingorwalkingwithhorse', 'strummingguitar'},

    'blues': {'arrangingflowers', 'brushinghair', 'claypotterymaking', 'cookingegg', 'crawlingbaby', 'dining',
              'discgolfing', 'drivingcar', 'egghunting', 'flippingpancake', 'golfchipping', 'golfdriving',
              'groominghorse', 'hoverboarding', 'hugging', 'iceskating', 'laughing', 'makingacake', 'newsanchoring',
              'pettinganimal(notcat)', 'pettingcat', 'playingaccordion', 'playingcards', 'playingflute',
              'playingguitar', 'playingharmonica', 'playingxylophone', 'shufflingcards', 'snorkeling', 'walkingthedog'},

    'reggae': {'blowingnose', 'bouncingontrampoline', 'canoeingorkayaking', 'catchingorthrowingfrisbee', 'trainingdog',
               'dancingmacarena', 'eatingburger', 'flyingkite', 'groomingdog', 'holdingsnake', 'hopscotch', 'jetskiing',
               'passingAmericanfootball(notingame)', 'playingbadminton', 'playingdidgeridoo', 'playingkickball',
               'playingtennis', 'playingukulele', 'smokinghookah', 'smoking', 'spinningpoi', 'surfingwater', 'capoeira'}
}


def get_track_path(label):
    if label == 'None':
        return random.choice(glob.glob(f'{os.environ.get("MUSIC_DATA")}/pop/*'))
    else:
        for key, val in GENRES.items():
            if label in val:
                return random.choice(glob.glob(f'{os.environ.get("MUSIC_DATA")}/{key}/*'))
