import flet as ft
import db_model
import env
from operator import attrgetter

import asyncio

import threading
change_page_lock = threading.Lock()

PAGE_TITLE="rawscraping"
TITLE_NUM_PER_PAGE = 16


class PageUpdateRow(ft.Row):
    def __init__(self):
        super().__init__()
        self.running = False
        self.progress_bar = ft.ProgressBar(width=200, visible=False)
        self.label = ft.Text("", visible=False)
        self.update_button = ft.IconButton(icon=ft.Icons.ARROW_CIRCLE_DOWN, on_click=self.on_click_update)
        self.controls = [self.update_button, self.progress_bar, self.label]

    def on_click_update(self, e):
        self.running = True
        self.page.run_task(self.run)
        self.page.update()
        db_model.update_all_pages()
        self.running = False

    async def run(self):
        self.progress_bar.value = 0
        self.progress_bar.visible = True
        self.progress_bar.update()
        self.label.visible = True
        self.label.update()
        self.update_button.visible = False
        while self.running:
            now = db_model.update_page_now
            max = db_model.update_page_max
            self.progress_bar.value = now / max
            self.progress_bar.update()
            self.label.value = f"Updating: {now}/{max}"
            self.label.update()
            self.page.update()
            await asyncio.sleep(0.3)
        self.progress_bar.visible = False
        self.progress_bar.update()
        self.label.visible = False
        self.label.update()
        self.update_button.visible = True
        self.update_button.update()
        self.page.update()

def main(page: ft.Page):
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
            #webbrowser.open(env.BASE_URL+url)
            nonlocal page
            page.launch_url(env.BASE_URL+url)

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
        card_image = None
        enable_base64 = True
        if enable_base64:
            #req = requests.get(image_src)
            #image_base64 = base64.b64encode(req.content).decode()
            image_base64 = db_model.get_base64(img)
            card_image = ft.Image(src_base64=image_base64, width=150)
        else :
            card_image = ft.Image(src=image_src, width=150)
        card = ft.Card(
            content=ft.Row([
                favorite,
                ft.Container(content=card_image, on_click=on_click_web),
                ft.Column([
                    ft.TextButton(title_name, on_click=on_click_web, expand=True, ),
                    ft.Text(f"{updated.split(' ')[0]} {latest}"),
                ], expand=True, alignment=0 ),
            ],), 
        )
        #page.add(title)
        return card

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
        nonlocal start_page
        nonlocal search_input
        search_input.value=""
        search_input.update()
        favorite = False
        start_page = 0
        grid_view_update()
        change_page_label()
        
    def on_search_submit(e):
        update_titles()
        nonlocal titles
        nonlocal grid_view
        nonlocal search_input
        if search_input.value == "":
            grid_view_update()
        else:
            grid_view.controls = []
            for title in titles:
                if search_input.value in title.name:
                    grid_view.controls.append(create_title(title))
            grid_view.update()

    def change_page(delta=0):
        with change_page_lock:
            nonlocal titles
            nonlocal start_page
            start_page = start_page + delta

            if start_page < 0:
                start_page = 0
            if start_page > len(titles):
                start_page = len(titles) - TITLE_NUM_PER_PAGE
            grid_view_update()
            #print(e.key, e.shift, e.ctrl, e.alt, e.meta)
            nonlocal favorite
            if not favorite:
                change_page_label()
        
    def on_keyboard_event(e:ft.KeyboardEvent):
        if (e.key=="Arrow Up" or e.key=="Arrow Left"):
            change_page(-TITLE_NUM_PER_PAGE)
        if (e.key=="Arrow Down" or e.key=="Arrow Right"):
            change_page(TITLE_NUM_PER_PAGE)

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

    def on_click_next_page(e):
        change_page(TITLE_NUM_PER_PAGE)
        
    def on_click_preview_page(e):
        change_page(-TITLE_NUM_PER_PAGE)

    def on_change_end_slider(e):
        nonlocal page_slider
        nonlocal start_page
        start_page = int(page_slider.value) * TITLE_NUM_PER_PAGE
        change_page(0)

    favorite = False
    start_page = 0
    page.on_keyboard_event=on_keyboard_event
    page.scroll = ft.ScrollMode.ALWAYS
    star_button = ft.IconButton(icon=ft.Icons.STAR, on_click=on_click_star)
    home_button = ft.IconButton(icon=ft.Icons.OTHER_HOUSES, on_click=on_click_home)
    search_input = ft.TextField(label="search", on_submit=on_search_submit)
    next_page_button = ft.IconButton(icon=ft.Icons.ARROW_RIGHT, on_click=on_click_next_page)
    preview_page_button = ft.IconButton(icon=ft.Icons.ARROW_LEFT, on_click=on_click_preview_page)
    page_updater = PageUpdateRow()


    grid_view = ft.GridView(expand=1, runs_count=5, max_extent=600, child_aspect_ratio=1.5, spacing=5, run_spacing=5)
    titles = db_model.get_all()
    titles.sort(key=attrgetter('updated'), reverse=True)
    page_label = ft.Text("")

    max_pages = int((len(titles)+TITLE_NUM_PER_PAGE-1)/TITLE_NUM_PER_PAGE)
    page_slider = ft.Slider(value=1, min=1, max=max_pages, divisions=max_pages, label="{value}", on_change=on_change_end_slider)

    page.add(ft.Row([star_button, home_button, search_input, page_label, page_slider, page_updater]))
    page.add(ft.Row([preview_page_button, grid_view, next_page_button]))
    grid_view_update()
    change_page_label()
    page.title=PAGE_TITLE
    page.update()
    
ft.app(main)