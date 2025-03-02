import flet as ft
import db_model
import webbrowser
import env

def create_title(page: ft.Page, name, img, url, fav, latest, updated):
    def on_click_fav(e):
        nonlocal favorite
        if favorite.icon is ft.Icons.STAR:
            favorite.icon = ft.Icons.STAR_BORDER
            fav = 0
        else:
            favorite.icon = ft.Icons.STAR
            fav = 1
        e.control.update()
        db_model.set_favorite_by_name(name, fav)

    def on_click_web(e):
        nonlocal url
        webbrowser.open(env.BASE_URL+url)

    image_src= env.BASE_URL + img
    title_name=name
    if title_name.endswith(" Raw Free"):
        title_name = title_name[:-len(" Raw Free")]
    favorite = ft.IconButton(icon=ft.Icons.STAR, on_click=on_click_fav)
    if fav != 1:
        favorite.icon = ft.Icons.STAR_BORDER

    title = ft.Card(
        content=ft.Row([
            favorite,
            ft.Container(content=ft.Image(src=image_src, width=100), on_click=on_click_web),
            ft.TextButton(title_name, on_click=on_click_web, expand=True),
        ]), 
    width=400)
    #page.add(title)
    return title

def main(page: ft.Page):
    page.title = "rawscraping"
    page.scroll = ft.ScrollMode.ALWAYS
    grid_view = ft.GridView(expand=1, runs_count=5, max_extent=400, child_aspect_ratio=1.0, spacing=5, run_spacing=5)
    for i in range(100):
        id = i+1 
        db_id, db_name, db_url, db_img, db_latest, db_favorite, db_updated = db_model.get_title(id)
        grid_view.controls.append(create_title(page, db_name, db_img, db_url, db_favorite, db_latest, db_updated))

    page.add(grid_view)

    
ft.app(main)