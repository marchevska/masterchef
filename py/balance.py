#!/usr/bin/env python

import scraft
from scraft import engine as oE
from Tkinter import *
import Image, ImageTk, tkFont
import string, traceback
import globalvars
import defs

MAX_RECIPES = 5
MAX_RECIPES_IN_SETTING = 15
MAX_INGREDIENTS = 10
MAX_ING_IN_RECIPE = 6
MIN_DIFF = 1.0
ZEROSTRING = ""
ZEROVALUE = 0
NONZEROVALUE = 1
ICON_HEIGHT = 15

class Application(Frame):
    def createWidgets(self):
        #recipes list
        
        self.Frame0 = Frame(self, borderwidth = 1, relief = GROOVE)
        self.Frame0.grid(row=0, column=0, rowspan = 3, sticky = NW, ipadx = 0, ipady = 0, padx = 1, pady = 1)
        self.Frame0.Elements = {}
        
        self.Frame0.Elements["text"] = Text(self.Frame0, width=36, height=31, 
                                            bg="lightgrey", relief = FLAT)
        self.Frame0.Elements["text"].grid(row=0, column=0, sticky = NW)
        self.Frame0.Elements["frame"] = Frame(self.Frame0.Elements["text"])
        self.Frame0.Elements["text"].window_create(END, window = self.Frame0.Elements["frame"])
        
        self.Frame0.Elements["cuisines"] = Label(self.Frame0.Elements["frame"], text = "Select cuisine:")
        self.Frame0.Elements["cuisines"].grid(row=0, column=0, columnspan=2, sticky = W, ipadx = 3, ipady = 1, padx = 1, pady = 1)
        for i in range(len(AllSettings)):
            self.Frame0.Elements["radio"+str(i)] = Radiobutton(self.Frame0.Elements["frame"],
                value = AllSettings[i], text = AllSettings[i], variable = CurrentSetting, command = self.ResetCuisine)
            self.Frame0.Elements["radio"+str(i)].grid(row=i+1, column=0, columnspan=2, sticky = W)
        fnt = tkFont.Font (family="Verdana", size=-(ICON_HEIGHT-2))
        self.Frame0.Elements["listbox"] = Listbox(self.Frame0.Elements["frame"], width=15, height=MAX_RECIPES_IN_SETTING,
                                            selectmode = MULTIPLE, font = fnt)
        self.Frame0.Elements["listbox"].grid(row=10, column=0, rowspan=MAX_RECIPES_IN_SETTING, sticky = NW)
        for i in range(MAX_RECIPES_IN_SETTING):
            self.Frame0.Elements["recipe"+str(i)] = Frame(self.Frame0.Elements["frame"])
            self.Frame0.Elements["recipe"+str(i)].grid(row=i+10, column=1, sticky = NW, ipadx = 0, ipady = 0, padx = 5, pady = 0)
        self.ResetCuisine()
            
        self.Frame0.Elements[0,1] = Button(self.Frame0, text = "Select recipes", command = self.selectRcp)    
        self.Frame0.Elements[0,1].grid(row=1, column=0, ipadx = 3, ipady = 1, padx = 5, pady = 1, sticky=N+S)
        
        #input field size
        self.Frame1 = Frame(self, borderwidth = 1, relief = GROOVE)
        self.Frame1.grid(row=0, column=1, columnspan = 2, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
        self.Frame1.Elements = {}
        self.Frame1.Elements[0] = Label(self.Frame1, text = "Field size:")
        self.Frame1.Elements[0].grid(row=0, column=0, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
        self.Frame1.Elements[1] = Entry(self.Frame1, textvariable = FieldSize[0], width = 2)
        self.Frame1.Elements[1].grid(row=0, column=1, sticky = W, ipadx = 1, ipady = 1, padx = 1, pady = 1)
        self.Frame1.Elements[2] = Label(self.Frame1, text = "x")
        self.Frame1.Elements[2].grid(row=0, column=2, sticky = W, ipadx = 1, ipady = 1, padx = 1, pady = 1)
        self.Frame1.Elements[3] = Entry(self.Frame1, textvariable = FieldSize[1], width = 2)
        self.Frame1.Elements[3].grid(row=0, column=3, sticky = W, ipadx = 1, ipady = 1, padx = 1, pady = 1)
        
        #select desired recipe rates
        self.Frame2 = Frame(self, borderwidth = 1, relief = GROOVE)
        self.Frame2.grid(row=1, column=1, columnspan = 2, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
        self.Frame2.Elements = {}
        
        self.Frame2.columnconfigure(2,minsize=160)
        #labels
        tmpLabels = ("Recipes", "Rate", "Use", "Diff")
        for j in range(len(tmpLabels)):
            self.Frame2.Elements[j, 0] = Label(self.Frame2, text = tmpLabels[j])
            self.Frame2.Elements[j, 0].grid(row=0, column=j, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
            
        for i in range(MAX_RECIPES):
            self.Frame2.Elements[0, i+1] = Label(self.Frame2, textvariable = Recipes[i], anchor = W, relief = SUNKEN, width = 20)
            self.Frame2.Elements[0, i+1].grid(row=i+1, column=0, ipadx = 3, ipady = 1, padx = 5, pady = 3)
            self.Frame2.Elements[1, i+1] = Entry(self.Frame2, textvariable = RecipeRates[i], width = 3)
            self.Frame2.Elements[1, i+1].grid(row=i+1, column=1, ipadx = 3, ipady = 1, padx = 5, pady = 3)
            self.Frame2.Elements[3, i+1] = Label(self.Frame2, textvariable = RecipeDiffs[i], anchor = W, relief = SUNKEN, width = 5)
            self.Frame2.Elements[3, i+1].grid(row=i+1, column=3, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 3)
            self.Frame2.Elements[2, i+1] = Frame(self.Frame2, relief = SUNKEN)
            self.Frame2.Elements[2, i+1].grid(row=i+1, column=2, sticky = W, ipadx = 3, ipady = 0, padx = 5, pady = 0)
            
        self.Frame3 = Frame(self, borderwidth = 1, relief = GROOVE)
        self.Frame3.grid(row=2, column=1, columnspan = 2, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
        self.Frame3.Elements = {}
            
        #view ingredients
        tmpLabels = ("Ingredients", "Ideal", "User", "Av.Group")
        for j in range(len(tmpLabels)):
            self.Frame3.Elements[j, 0] = Label(self.Frame3, text = tmpLabels[j])
            self.Frame3.Elements[j, 0].grid(row=0, column=j, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
            
        for i in range(MAX_INGREDIENTS):
            self.Frame3.Elements[0, i+1] = Label(self.Frame3, textvariable = Ingredients[i], relief = SUNKEN, width = 20)
            self.Frame3.Elements[0, i+1].grid(row=i+1, column=0, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
            self.Frame3.Elements[1, i+1] = Label(self.Frame3, textvariable = IngredIdeal[i], relief = SUNKEN, width = 3)
            self.Frame3.Elements[1, i+1].grid(row=i+1, column=1, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
            self.Frame3.Elements[2, i+1] = Entry(self.Frame3, textvariable = IngredUser[i], width = 3)
            self.Frame3.Elements[2, i+1].grid(row=i+1, column=2, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
            self.Frame3.Elements[3, i+1] = Label(self.Frame3, textvariable = IngredGroup[i], anchor = W, relief = SUNKEN, width = 5)
            self.Frame3.Elements[3, i+1].grid(row=i+1, column=3, sticky = W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
            
        #buttons at the bottom
        self.Frame4 = Frame(self, borderwidth = 1, relief = GROOVE)
        self.Frame4.grid(row=3, column=0, columnspan = 3, sticky = E+W, ipadx = 3, ipady = 1, padx = 5, pady = 1)
        self.Frame4.Elements = {}
        self.Frame4.Elements[0] = Button(self.Frame4, text = "Calculate ingredients", command = self.calcIng)    
        self.Frame4.Elements[0].grid(row=0, column=0, ipadx = 3, ipady = 1, padx = 5, pady = 1)
        self.Frame4.Elements[1] = Button(self.Frame4, text = "Set ideal rates", command = self.setIdeal)    
        self.Frame4.Elements[1].grid(row=0, column=1, ipadx = 3, ipady = 1, padx = 5, pady = 1)
        self.Frame4.Elements[2] = Button(self.Frame4, text = "Calculate difficulties", command = self.calcDiff)    
        self.Frame4.Elements[2].grid(row=0, column=2, ipadx = 3, ipady = 1, padx = 5, pady = 1)
        
        

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    #chooses recipes from specified episode
    def ResetCuisine(self):
        global CurrentRecipes
        CurrentRecipes = filter(lambda x: globalvars.CuisineInfo.GetTag("Recipes").GetSubtag(x).GetStrAttr("setting") == CurrentSetting.get(), AllRecipes)
        self.Frame0.Elements["listbox"].delete(0, self.Frame0.Elements["listbox"].size()-1)
        for tmp in CurrentRecipes:
            self.Frame0.Elements["listbox"].insert("end", tmp)
        #draw ingerients icons!
        for i in range(len(CurrentRecipes)):
            rcp = CurrentRecipes[i]
            tmpIngRequired = eval(globalvars.CuisineInfo.GetTag("Recipes").GetSubtag(rcp).GetStrAttr("requires"))
            self.Frame0.Elements["ingred"+str(i)] = {}
            j = 0
            for ing in tmpIngRequired.keys():
                try:
                    im = Image.open("img/ingredients/"+ing+".icon.png")
                    im = im.resize((ICON_HEIGHT-2,ICON_HEIGHT-3))
                    if im.mode == "1":
                        self.Frame0.Elements["ingred"+str(i)][j, "img"] = ImageTk.BitmapImage(im)
                    else:
                        self.Frame0.Elements["ingred"+str(i)][j, "img"] = ImageTk.PhotoImage(im)
                    self.Frame0.Elements["ingred"+str(i)][j] = Label(self.Frame0.Elements["recipe"+str(i)],
                                                image = self.Frame0.Elements["ingred"+str(i)][j, "img"])
                    self.Frame0.Elements["ingred"+str(i)][j].grid(row=0, column=j, sticky = NW)
                    j+=1
                except:
                    pass
        for i in range(len(CurrentRecipes), MAX_RECIPES_IN_SETTING):
            self.Frame0.Elements["ingred"+str(i)] = {}
            
        
    def setIdeal(self):
        self.calcIng()
        for i in range(MAX_INGREDIENTS):
            IngredUser[i].set(IngredIdeal[i].get())
        
    #calculate desired ingredients
    def calcIng(self):
        #clear existing images
        try:
            for i in range(MAX_RECIPES):
                if self.Frame2.Elements.has_key((2, i+1, "ing")):
                    for j in range(MAX_ING_IN_RECIPE):
                        if self.Frame2.Elements[2, i+1, "ing"].has_key(j):
                            self.Frame2.Elements[2, i+1, "ing"][j].grid_forget()
        except:
            pass
        tmpAllRcp = []
        for i in range(MAX_RECIPES):
            if Recipes[i].get()!=ZEROSTRING:
                tmpAllRcp.append(Recipes[i].get())
        tmpIngIdeal = dict(map(lambda x: (x,0), AllIngredients))
        for i in range(len(tmpAllRcp)):
            rcp = tmpAllRcp[i]
            tmpIngRequired = eval(globalvars.CuisineInfo.GetTag("Recipes").GetSubtag(rcp).GetStrAttr("requires"))
            self.Frame2.Elements[2, i+1, "ing"] = {}
            j = 0
            for ing in tmpIngRequired.keys():
                tmpIngIdeal[ing] += tmpIngRequired[ing]*RecipeRates[i].get()
                #draw ingredient image!
                try:
                    im = Image.open("img/ingredients/"+ing+".icon.png")
                    if im.mode == "1":
                        self.Frame2.Elements[2, i+1, "ing"][j, "img"] = ImageTk.BitmapImage(im)
                    else:
                        self.Frame2.Elements[2, i+1, "ing"][j, "img"] = ImageTk.PhotoImage(im)
                    self.Frame2.Elements[2, i+1, "ing"][j] = Label(self.Frame2.Elements[2, i+1],
                                                image = self.Frame2.Elements[2, i+1, "ing"][j, "img"])
                    self.Frame2.Elements[2, i+1, "ing"][j].grid(row=0, column=j)
                    j+=1
                except:
                    pass
                
        tmpIngNonZero = filter(lambda x: tmpIngIdeal[x]!=0, tmpIngIdeal.keys())
        for i in range(len(tmpIngNonZero)):
            Ingredients[i].set(tmpIngNonZero[i])
            IngredIdeal[i].set(tmpIngIdeal[tmpIngNonZero[i]])
        for i in range(len(tmpIngNonZero), MAX_INGREDIENTS):
            Ingredients[i].set(ZEROSTRING)
            IngredIdeal[i].set(ZEROVALUE)

    
    def calcDiff(self):
        try:
            filename = "balance/"+str(FieldSize[0].get())+"x"+str(FieldSize[1].get())+".def"
            tmpGroups = defs.ReadGroups(filename)
            tmpKnownRates = tmpGroups.keys()
            tmpAllUserRates = map(lambda x: x.get(), IngredUser)
            tmpSumRates = reduce(lambda a,b: a+b, tmpAllUserRates, 0)
            #calculate group sizes
            if tmpSumRates>0 and tmpKnownRates!=[]:
                for i in range(MAX_INGREDIENTS):
                    tmpRate = 1.0*tmpAllUserRates[i]/tmpSumRates
                    tmp1 = filter(lambda x: x<=tmpRate, tmpKnownRates)
                    tmp1.sort()
                    tmpLessRate = tmp1[-1]
                    tmp2 = filter(lambda x: x>=tmpRate, tmpKnownRates)
                    tmp2.sort()
                    tmpHigherRate = tmp2[0]
                    if tmpHigherRate > tmpLessRate:
                        tmpGroupSize = tmpGroups[tmpLessRate] + \
                            (tmpRate-tmpLessRate)*(tmpGroups[tmpHigherRate]-tmpGroups[tmpLessRate])/(tmpHigherRate-tmpLessRate)
                    else:
                        tmpGroupSize = tmpGroups[tmpLessRate]
                    tmpGroupSize = int(tmpGroupSize*1000)*0.001
                    IngredGroup[i].set(tmpGroupSize)
                #calculate recipe difficulties
                tmpAllIngredients = map(lambda x: x.get(), Ingredients)
                for i in range(MAX_RECIPES):
                    tmpDiff = 0
                    tmpRcp = Recipes[i].get()
                    if tmpRcp != ZEROSTRING:
                        tmpIngRequired = eval(globalvars.CuisineInfo.GetTag("Recipes").GetSubtag(tmpRcp).GetStrAttr("requires"))
                        for ing in tmpIngRequired.keys():
                            ind = tmpAllIngredients.index(ing)
                            tmpDiff += max(1.0*tmpIngRequired[ing]/IngredGroup[ind].get(), MIN_DIFF)
                        tmpDiff = int(1000*tmpDiff)*0.001
                        RecipeDiffs[i].set(tmpDiff)
        except:
            print unicode(string.join(apply(traceback.format_exception, sys.exc_info())))
            pass
        
    #copy recipes from listbox to a list
    def selectRcp(self):
        global CurrentRecipes
        tmpInd = list(self.Frame0.Elements["listbox"].curselection())
        for i in range(len(tmpInd)):
            Recipes[i].set(CurrentRecipes[eval(tmpInd[i])])
            if not RecipeRates[i].get():
                RecipeRates[i].set(NONZEROVALUE)    
        for i in range(len(tmpInd), MAX_RECIPES):
            Recipes[i].set(ZEROSTRING)
            RecipeRates[i].set(ZEROVALUE)    
        

defs.ReadCuisine()
defs.ReadResourceInfo()

AllRecipes = map(lambda x: x.GetContent(), globalvars.CuisineInfo.GetTag("Recipes").Tags())
AllRecipes.sort()
AllSettings = ["Japanese", "Mexican", "Rusian", "Hawaiian", "American"]
AllIngredients = map(lambda x: x.GetContent(), globalvars.CuisineInfo.GetTag("Ingredients").Tags())
AllIngredients.sort()
CurrentRecipes = []

root = Tk()

Recipes = map(lambda x: StringVar(), xrange(MAX_RECIPES))
RecipeRates = map(lambda x: IntVar(), xrange(MAX_RECIPES))
RecipeDiffs = map(lambda x: DoubleVar(), xrange(MAX_RECIPES))
Ingredients = map(lambda x: StringVar(), xrange(MAX_INGREDIENTS))
IngredIdeal = map(lambda x: IntVar(), xrange(MAX_INGREDIENTS))
IngredUser = map(lambda x: IntVar(), xrange(MAX_INGREDIENTS))
IngredGroup = map(lambda x: DoubleVar(), xrange(MAX_INGREDIENTS))
FieldSize = map(lambda x: IntVar(), xrange(2))

CurrentSetting = StringVar()
CurrentSetting.set(AllSettings[0])

root.wm_resizable(width=False, height=False)

app = Application(master=root)
app.master.title("MasterChef Level Difficulty Estimation")

app.mainloop()

