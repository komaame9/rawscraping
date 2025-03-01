import flet as ft
import db_model
import webbrowser
import env

def create_title(page: ft.Page, name, img, url, fav):
    def on_click_fav(e):
        nonlocal favorite
        if favorite.icon is ft.Icons.STAR:
            favorite.icon = ft.Icons.STAR_BORDER
        else:
            favorite.icon = ft.Icons.STAR
        e.control.update()

    def on_click_web(e):
        nonlocal url
        webbrowser.open(env.BASE_URL+url)

    print(img)
    image_src= env.BASE_URL + img
    title_name=name
    favorite = ft.IconButton(icon=ft.Icons.STAR, on_click=on_click_fav)
    title = ft.Row([
        ft.Image(src=image_src),
        ft.TextButton(title_name, on_click=on_click_web),
        favorite,
        ])
    page.add(title)

def main(page: ft.Page):
    page.title = "rawscraping"
    page.scroll = ft.ScrollMode.ALWAYS
    for i in range(100):
        id = i+1 
        db_id, db_name, db_url, db_img, db_latest, db_favorite, db_updated = db_model.get_title(id)
        create_title(page, db_name, db_img, db_url, db_favorite)

    
ft.app(main)