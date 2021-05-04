import math
import copy
from collections import defaultdict 


DEFAULT_PARAMS = {
  'base': math.e,
  'perf': 400,
  'kFactor': 32,
  'min': False,
  'max': False
}

class Elo:
  """
  A class that represents an implementation of the Elo Rating System
  """

  def __init__(self, setParams = {}):
    params = { **DEFAULT_PARAMS, **setParams }
    self.base = params['base']
    self.perf = params['perf']
    self.kFactor = params['kFactor']
    self.min = params['min']
    self.max = params['max']

  """
  Determines the expected "score" of a match

  @param {Number} rating The rating of the person whose expected score we're looking for, e.g. 1200
  @param {Number} opponentRating the rating of the challening person, e.g. 1200
  @return {Number} The score we expect the person to recieve, e.g. 0.5

  @link http://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details
  """
  def expectedScore(self, rating, opponentRating):
    difference =  opponentRating - rating
  
    return 1/(1 + 10**(difference/400.0))

  """
  Returns an array of anticipated scores for both players

  @param {Number} player1Rating The rating of player 1, e.g. 1200
  @param {Number} player2Rating The rating of player 2, e.g. 1200
  @return {Array} The anticipated scores, e.g. [0.25, 0.75]
  """
  def bothExpectedScores(self, player1Rating, player2Rating):
    return [
      self.expectedScore(player1Rating, player2Rating),
      self.expectedScore(player2Rating, player1Rating)
    ]

  """
  The calculated new rating based on the expected outcone, actual outcome, and previous score
  @param {Number} rating The current rating of the player, e.g. 1200
  @param {Number} expectedScore The expected score, e.g. 0.25
  @param {Number} actualScore The actual score, e.g. 1
  @return {Number} The new rating of the player, e.g. 1256
  """
  def newRating(self, rating, expectedScore, actualScore, kFactor):
    
    difference = actualScore - expectedScore

    newRating = rating + (kFactor * difference)

    if (self.min & (newRating < self.min)):
      newRating = self.min
    elif (self.max & (rating > self.max)):
      newRating = self.max

    return newRating
  
  """
  Internal function for initializaing the 
  @param {Boolean} item whether the model includes items
  @param {Boolean} concepts whether the model includes concepts
  @return Nothing
  """
  def initalizeModel(self, data, user_id):
    data = copy.deepcopy(data)
    self.predictions = {}
    items = data['items'] if 'items' in data else {}
    concepts = data['concepts'] if 'concepts' in data else {}
    
    default_user = {
        'user_id': user_id,
        'rating': 1000,
        'count': 0
    }
    
    if('user' in data):
        user = {**default_user, **data['user']}
    
    user['concepts'] = defaultdict(lambda: {
          'rating': 1000,
          'count': 0
    }, user['concepts'] if 'concepts' in user else {})
    
    
    self.users = {}
    self.users[user_id] = user

    self.predictions['item'] = []
    self.items = defaultdict(lambda: {
          'rating': 1000,
          'count': 0
    }, items)
    
    self.predictions['concepts'] = []
    self.concepts = defaultdict(lambda: {
          'rating': 1000,
          'count': 0
    }, concepts)

  """
  Calculate expected scores of concepts
  @param {Object} user reference to user object
  @param {List} concepts keys of the concepts
  @return self
  """
  def expectedScoreConcept(self, user, concepts):
    ### Concept difficulty: User's Concept Knowledge vs Global Concept Difficulty Rating
    #
    p_concepts = {}
    # Makes a prediction for each concept in activity
    for concept in concepts:
        p_concepts[concept] = self.expectedScore(user['concepts'][concept]['rating'], self.concepts[concept]['rating'])
    # Averages all predictions
    return p_concepts
    #
    ###

  """
  Update scores based on user matching with an item
  @param {tuple} match match information
  @param {Float} p_item expected score of matchup
  @return self
  """
  def updateItem(self, match, p_item):
    _user = self.users[match['user']]
    _item = self.items[match['item']]

    _item['rating'] = self.newRating(
      _item['rating'], 
      1 - p_item, 
      1 - match['result'], 
      self.uncertainty(_item['count'])
    )
    _item['count'] += 1
    
    # User rating - Exact same as above
    _user['rating'] = self.newRating(
      _user['rating'], 
      p_item, 
      match['result'], 
      self.uncertainty(_user['count']))
    _user['count'] += 1

  """
  Update scores based on user matching with a group of concepts
  @param {tuple} match match information
  @param {Object} p_concepts expected scores for each concept
  @return self
  """
  def updateConcepts(self, match, p_concepts):
    _user = self.users[match['user']]

    # Concept difficulty rating - Scoped user concept knowledge vs Concept difficulty rating
    for con in p_concepts:
        self.concepts[con]['rating'] = self.newRating(self.concepts[con]['rating'], 1 - p_concepts[con], 1 - match['result'], self.uncertainty(self.concepts[con]['count']))
        self.concepts[con]['count'] +=1
        
    # User knowledge of concepts
    for con in p_concepts:
        _user['concepts'][con]['rating'] = self.newRating(_user['concepts'][con]['rating'], p_concepts[con], match['result'], self.uncertainty(_user['concepts'][con]['count']))
        _user['concepts'][con]['count'] +=1

  """
  Run an Elo student model on a dataframe
  @param {DataFrame} data The input for the model
  @param {String} result column name of result
  @param {String} user column name of user
  @param {String} item column name of item
  @param {String} concepts column name of concepts
  @return self
  """
  def run(self, result, user, item=False, concepts=False, data = {}):
    if((item == False) & (concepts == False)):
      print('Must provide at least item or concept')
    

    self.initalizeModel(data, user)
    columns = [x for x in [result, user, item, concepts] if x != False]
    
    match = {'result': result, 'user': user, 'item': item, 'concepts': concepts}

    ###
    # Calculate predictions
    ###
    p_item = False
    p_concepts = False

    if(item): 
        p_item = self.expectedScore(self.users[user]['rating'], self.items[item]['rating'])
        self.predictions['item'].append(p_item)

    if(concepts): 
        p_concepts = self.expectedScoreConcept(self.users[user], concepts)
        self.predictions['concepts'].append(sum(p_concepts.values()) /len(p_concepts))

    ###
    # Calculate Rating updates, collect counts for uncertainty function
    ###

    # User vs Item 
    if(p_item): self.updateItem(match, p_item)

    if(p_concepts): self.updateConcepts(match, p_concepts)

      

    return self


  """
  The calculated new rating based on the expected outcone, actual outcome, and previous score
  @param {Number} numOfProblems The number of problems attempted, e.g. 10
  @param {Number} a scaling meta-parameter 
  @param {Number} b scaling meta-paramter
  @return {Number} KFactor the kfactor to use based on user
  """
  def uncertainty(self, n, a = 1, b = .05):
    return (a / (1 + b*n)) * self.kFactor
  
  #End class
