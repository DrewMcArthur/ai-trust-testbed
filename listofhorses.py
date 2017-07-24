import pickle 
import os

horses = pickle.load(open('listOfNiceRaces.pkl', 'rb'))
sixtonine = []
print(len(horses))
for horse in horses:
	if os.path.isfile(os.path.join('split',horse+'_8.pdf')) and not os.path.isfile(os.path.join('split',horse+'_9.pdf')):
		sixtonine.append(horse)
		print(horse)
#pickle.dump(sixtonine, open('sixtonine.pkl','wb'))
print(len(sixtonine))