# Importing modules to be used:
# tk and ttk are used for widget combinations that differ in form and function
# filedialog summons a box that allows users to interact with files, and save them in our case
# PIL is used to load images
# font_manager manages fonts, and displays them
# requests allows API functionality

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib import font_manager
import requests

# Locating fonts with font_manager

font_manager.findSystemFonts(fontpaths=None, fontext="ttf")
font_manager.findfont("maki_maruhand")

# Setting up the window
root = tk.Tk()
root.title("Recipe Finder")
root.geometry("1280x720")

# Setting up custom style for buttons
style = ttk.Style()
style.theme_use("alt")
style.configure("TButton", background = "#f5ebdc", foreground = "#664718", width = 20, borderwidth=1, focusthickness=1, focuscolor="none")
style.map("TButton")

# Title of the program, on the bottom left corner
title = tk.Label(root, text="Recipe Finder", font=("maki_maruhand", 40, "bold"), bg="#ffffff", fg="#80634e")
title.place(relx=0.05, rely=0.95, anchor="sw")

#########################################
# -- Part 1/2: defining our functions --#
#########################################

# We will attempt to retrieve recipe data from the API and save it in a variable.
# As well as the recipe images.

def fetch_recipe(query):
    # Fetch response with .get function, then store in var "data" with .json function.
    api = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    res = requests.get(api)
    data = res.json()

    # Verify res by recalling the string "meals" found in the response.
    # Then save "strMeal", where the recipe names are located, in var "recipes".
    if "meals" in data and data["meals"] is not None:
        recipes = [meal["strMeal"] for meal in data["meals"]]
        return recipes
    else:
    # Extra condition check.
        return ["No recipe found."]

def fetch_recipe_image(query):
    # Same process as fetch_recipe(), but with the recipe image.
    api = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    res = requests.get(api)
    data = res.json()

    if "meals" in data and data["meals"]:
        meal = data["meals"][0]
        image_url = meal.get("strMealThumb", "")
        return image_url
    else:
        return ""

def fetch_recipe_details(query):
    # Fetch recipe details.
    api = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    res = requests.get(api)
    data = res.json()

    # And format the data so that it will be presented nicely.
    if "meals" in data and data["meals"]:
        meal = data["meals"][0]
        details = f"Category: {meal['strCategory']}\n\nIngredients:\n"
        for i in range(1, 21):
            ingredient = meal[f'strIngredient{i}']
            measure = meal[f'strMeasure{i}']
            if ingredient and measure and ingredient != 'null' and measure != 'null':
                details += f"{ingredient} - {measure}\n"
        details += f"\nInstructions:\n{meal['strInstructions']}"
        return details
    else:
        return "Details not available."

# This gives the user the ability to browse recipes from a listbox.
    
def search_recipes():
    # Using .get() and .strip() functions to store what the user types in the search bar.
    query = search_entry.get().strip()
    if query:
        # If query is successful, listbox gets cleared.
        recipe_listbox.delete(0, tk.END)
        # And the following function is used to send the API our query as a request.
        recipes = fetch_recipe(query)
        # From all the available recipes, updates the listbox by showing each result with the var "recipe" in it.
        for recipe in recipes:
            recipe_listbox.insert(tk.END, recipe)

# This allows the image of the recipe and its details, such as the ingredients and measurements used, to be displayed.
            
def display_recipe_details(e):
    # Stores the user selection. When a recipe is clicked on, it is selected.
    selected_index = recipe_listbox.curselection()
    if selected_index:
        # Define it as the selected recipe.
        selected_recipe = recipe_listbox.get(selected_index)
        # Store the fetched recipe image and details.
        details = fetch_recipe_details(selected_recipe)
        image_url = fetch_recipe_image(selected_recipe)

        # Update the details section (textbox) on the right with new retrieved info.
        details_text.config(state=tk.NORMAL)
        details_text.delete(1.0, tk.END)
        details_text.insert(tk.END, details)
        details_text.config(state=tk.DISABLED)

    # Then load the recipe image, or clear it if it's not available.
    if image_url:
        image = Image.open(requests.get(image_url, stream=True).raw)
        image.thumbnail((200, 200))
        img = ImageTk.PhotoImage(image)
        recipe_image_label.configure(image=img)
        recipe_image_label.image = img
            
    else:
        recipe_image_label.configure(image="")
        recipe_image_label.image = None

# This shows a random recipe.
        
def show_random_recipe():
    # Works like fetch_recipe() and display_recipe_details(), combined into one.
    random_recipe_url = "https://www.themealdb.com/api/json/v1/1/random.php"
    res = requests.get(random_recipe_url)
    data = res.json()
    meal = data["meals"][0]
    details = f"Recipe: {meal['strMeal']}\n\nCategory: {meal['strCategory']}\n\nIngredients:\n"
    for i in range(1, 21):
        ingredient = meal[f'strIngredient{i}']
        measure = meal[f'strMeasure{i}']
        if ingredient and measure and ingredient != 'null' and measure != 'null':
            details += f"{ingredient} - {measure}\n"
    details += f"\nInstructions:\n{meal['strInstructions']}"

    details_text.config(state=tk.NORMAL)
    details_text.delete(1.0, tk.END)
    details_text.insert(tk.END, details)
    details_text.config(state=tk.DISABLED)

    image_url = meal.get("strMealThumb", "")

    if image_url:
        image = Image.open(requests.get(image_url, stream=True).raw)
        image.thumbnail((200, 200))
        img = ImageTk.PhotoImage(image)
        recipe_image_label.configure(image=img)
        recipe_image_label.image = img
            
    else:
        recipe_image_label.configure(image="")
        recipe_image_label.image = None

# Saves the recipe that's being displayed as of current.
def save_recipe():
    filetypes = [
    ("Text file - .txt", "*.txt", "TEXT"),
    ("All files", "*"),
    ]

    text_file = filedialog.asksaveasfile(initialfile = "Recipe", mode='w', defaultextension='.txt', filetypes=filetypes)
    text_file.write(details_text.get(1.0, tk.END))
    text_file.close()

######################################
# -- Part 2/2: Setting up the GUI -- #
######################################
    
# Sets the background image.
bg_image = Image.open("sumikko2.jpg")
bg_image = bg_image.resize((1280, 720))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# A search bar.
search_entry = tk.Entry(root, font=("Arial", 14), fg="#664718")
search_entry.place(relx=0.5, rely=0.1, relwidth=0.6, anchor="n")

# Search button that sends an API request with the search_recipes() function.
# Bound to the Enter key for convenience.
search_button = ttk.Button(root, text="Search Recipes", command=search_recipes)
search_button.place(relx=0.7, rely=0.1, relwidth=0.2, relheight=0.04, anchor="n")
root.bind('<Return>', lambda event: search_recipes())

# Recipe results appear here.
recipe_listbox = tk.Listbox(root, font=("Arial", 14), selectbackground="#664718", relief="flat", bg="#f5ebdc", fg="#664718")
recipe_listbox.place(relx=0.35, rely=0.2, relwidth=0.6, relheight=0.4, anchor="n")
recipe_listbox.bind("<ButtonRelease-1>", display_recipe_details)

# Recipe details appear here.
details_frame = tk.Frame(root, width=60, height=15, bg="#f5ebdc")
details_frame.place(relx=0.7, rely=0.2, relwidth=0.25, relheight=0.6)
details_frame.configure()

# Recipe image appears here.
recipe_image_label = tk.Label(details_frame, bg="#f5ebdc")
recipe_image_label.pack(pady=10)

# Label that displays the title text for recipe details.
details_label = tk.Label(details_frame, text="Recipe Details", font=("Arial", 14, "bold"), bg="#f5ebdc", fg="#664718")
details_label.pack(pady=5)

# Textbox where the recipe details are to be displayed.
details_text = tk.Text(details_frame, font=("Arial", 12), wrap="word", fg="#80634e", state=tk.DISABLED)
details_text.pack(expand=True, fill=tk.BOTH)

# Button to save a recipe.
save_button = ttk.Button(root, text="Save Recipe", command=save_recipe)
save_button.place(relx=0.95, rely=0.84, relwidth=0.25, relheight=0.04, anchor="se")

# Button that replaces the current recipe and info thereof with a random one.
random_recipe_button = ttk.Button(root, text="Random Recipe", command=show_random_recipe)
random_recipe_button.place(relx=0.95, rely=0.879, relwidth=0.25, relheight=0.04, anchor="se")

# Guiding text
help_text = tk.Label(root, text="Click on a recipe to view its details.", font=("Arial", 10, "bold"), bg="#ffffff", fg="#80634e")
help_text.place(relx=0.05, rely=0.63, anchor="sw")

# Lifts the title above the background to make it visible.
title.lift()

# Launches and runs the program indefinitely.
root.mainloop()