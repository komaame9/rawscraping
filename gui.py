import flet as ft
import db_model
import webbrowser
import env
from operator import attrgetter


def create_title(title: db_model.title):
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

    name = title.name
    url = title.url
    img = title.img
    fav = title.favorite
    updated = title.updated
    latest = title.latest
    
    image_src= env.BASE_URL + img
    title_name=name
    if title_name.endswith(" Raw Free"):
        title_name = title_name[:-len(" Raw Free")]
    favorite = ft.IconButton(icon=ft.Icons.STAR, on_click=on_click_fav)
    if fav != 1:
        favorite.icon = ft.Icons.STAR_BORDER

    card = ft.Card(
        content=ft.Row([
            favorite,
            ft.Container(content=ft.Image(src=image_src, width=150), on_click=on_click_web),
            ft.Column([
                ft.TextButton(title_name, on_click=on_click_web, expand=True, ),
                ft.Text(f"{updated.split(' ')[0]} {latest}"),
            ], expand=True, alignment=0 ),
        ],), 
    )
    #page.add(title)
    return card

TITLE_NUM_PER_PAGE = 6

def main(page: ft.Page):

    def update_titles():
        nonlocal titles
        titles = db_model.get_all()
        titles.sort(key=attrgetter('updated'), reverse=True)

    def grid_view_update():
        nonlocal favorite
        nonlocal titles
        nonlocal grid_view
        nonlocal start_page
        grid_view.controls = []
        if favorite:
            for title in titles:
                if  title.favorite == 1:
                    grid_view.controls.append(create_title(title))
        else:
            for i in range(TITLE_NUM_PER_PAGE):
                if (i+start_page) < len(titles):
                    grid_view.controls.append(create_title(titles[i+start_page]))
        grid_view.update()

    def on_click_star(e):
        update_titles()
        nonlocal favorite
        favorite = True
        grid_view_update()
        nonlocal page_label
        page_label.value =""
        page_label.update()

    def on_click_home(e):
        update_titles()
        nonlocal favorite
        favorite = False
        grid_view_update()
        change_page_label()
        
    def on_search_submit(e):
        update_titles()
        nonlocal titles
        nonlocal grid_view
        nonlocal search_input
        grid_view.controls = []
        for title in titles:
            if search_input.value in title.name:
                grid_view.controls.append(create_title(title))
        grid_view.update()

    def on_keyboard_event(e:ft.KeyboardEvent):
        nonlocal titles
        nonlocal start_page
        if (e.key=="Arrow Up" or e.key=="Arrow Right"):
            start_page = start_page - TITLE_NUM_PER_PAGE
        if (e.key=="Arrow Down" or e.key=="Arrow Left"):
            start_page = start_page + TITLE_NUM_PER_PAGE

        if start_page < 0:
            start_page = 0
        if start_page > len(titles):
            start_page = titles - TITLE_NUM_PER_PAGE
        grid_view_update()
        #print(e.key, e.shift, e.ctrl, e.alt, e.meta)
        nonlocal favorite
        if not favorite:
            change_page_label()
    def on_click_update(e):
        db_model.update_all_pages()

    def change_page_label():
        nonlocal start_page
        nonlocal page_label
        nonlocal favorite
        nonlocal titles
        title_num = len(titles)
        if (favorite):
            title_num = 0
            for title in titles:
                if title.favorite != 0:
                    title_num = title_num + 1
        page = int(start_page / TITLE_NUM_PER_PAGE)
        max_pages = int((title_num+TITLE_NUM_PER_PAGE-1)/TITLE_NUM_PER_PAGE)
        page_label.value = f"Page: {int(page+1)}/{int(max_pages)}"
        page_label.update()

    favorite = False
    start_page = 0
    page.on_keyboard_event=on_keyboard_event
    page.scroll = ft.ScrollMode.ALWAYS
    star_button = ft.IconButton(icon=ft.Icons.STAR, on_click=on_click_star)
    home_button = ft.IconButton(icon=ft.Icons.OTHER_HOUSES, on_click=on_click_home)
    search_input = ft.TextField(label="search", on_submit=on_search_submit)
    update_button = ft.IconButton(icon=ft.Icons.ARROW_CIRCLE_DOWN, on_click=on_click_update)


    grid_view = ft.GridView(expand=1, runs_count=5, max_extent=600, child_aspect_ratio=1.5, spacing=5, run_spacing=5)
    titles = []#db_model.get_all()
    titles.sort(key=attrgetter('updated'), reverse=True)
    page_label = ft.Text("")

    page.add(ft.Row([star_button, home_button, search_input, page_label, update_button]))
    page.add(grid_view)
    grid_view_update()
    change_page_label()
    page.update()

    with open('test.txt', mode="w") as f:
        f.write("this is test text")
    
ft.app(main)