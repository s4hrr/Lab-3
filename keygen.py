import os
import random
import shutil
import string
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox

BLOCKS = 3
BLOCK_LEN = 4
SUM_MIN = 40
SUM_MAX = 60

WEIGHTS = {}
for i, letter in enumerate(string.ascii_uppercase, start=1):
    WEIGHTS[letter] = i
for digit in string.digits:
    WEIGHTS[digit] = int(digit)

ALPHABET = list(WEIGHTS)


def block_sum(block):
    return sum(WEIGHTS[ch] for ch in block)


def generate_block():
    while True:
        block = ''.join(random.choice(ALPHABET) for _ in range(BLOCK_LEN))
        if SUM_MIN <= block_sum(block) <= SUM_MAX:
            return block


def generate_key():
    return '-'.join(generate_block() for _ in range(BLOCKS))


MUSIC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music.wav')
music_on = True
music_proc = None


def music_loop_mac():
    global music_proc
    while music_on:
        music_proc = subprocess.Popen(['afplay', MUSIC_FILE])
        music_proc.wait()


def start_music():
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play(-1)
        return
    except Exception:
        pass
    try:
        if sys.platform == 'win32':
            import winsound
            winsound.PlaySound(MUSIC_FILE, winsound.SND_ASYNC | winsound.SND_LOOP)
        elif shutil.which('afplay'):
            threading.Thread(target=music_loop_mac, daemon=True).start()
    except Exception:
        pass


def stop_music():
    global music_on
    music_on = False
    try:
        if music_proc:
            music_proc.terminate()
        if sys.platform == 'win32':
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass


def toggle_music():
    global music_on
    if music_on:
        stop_music()
        music_btn.configure(text='Музыка: выкл')
    else:
        music_on = True
        start_music()
        music_btn.configure(text='Музыка: вкл')


def on_exit():
    stop_music()
    window.destroy()


stars = []
shooting = {'id': None, 'x': 0, 'y': 0}
rolling = False


def make_stars():
    for _ in range(40):
        x, y = random.randint(0, 640), random.randint(0, 250)
        item = canvas.create_rectangle(x, y, x + 2, y + 2, fill='white', outline='')
        stars.append(item)


def animate():
    for item in stars:
        if random.random() < 0.2:
            canvas.itemconfigure(item, fill=random.choice(['white', '#ffe66d', '#8888aa', '#444466']))
    if shooting['id'] is None and random.random() < 0.05:
        shooting['x'], shooting['y'] = random.randint(250, 640), random.randint(0, 80)
        shooting['id'] = canvas.create_line(shooting['x'], shooting['y'],
                                            shooting['x'] + 14, shooting['y'] - 7,
                                            fill='white', width=2)
    elif shooting['id'] is not None:
        canvas.move(shooting['id'], -18, 9)
        shooting['x'] -= 18
        if shooting['x'] < -20:
            canvas.delete(shooting['id'])
            shooting['id'] = None
    window.after(120, animate)


def roll_key(final_key, step=0):
    global rolling
    rolling = True
    locked = step // 3
    shown = ''
    for i, ch in enumerate(final_key):
        if ch == '-' or i < locked:
            shown += ch
        else:
            shown += random.choice(ALPHABET)
    set_key_text(shown)
    if locked < len(final_key):
        window.after(40, roll_key, final_key, step + 1)
    else:
        rolling = False
        sums = '-'.join(str(block_sum(b)) for b in final_key.split('-'))
        sums_label.configure(text=f'Суммы блоков: {sums}  (интервал {SUM_MIN}…{SUM_MAX})')


def set_key_text(text):
    key_entry.configure(state='normal')
    key_entry.delete(0, tk.END)
    key_entry.insert(0, text)
    key_entry.configure(state='readonly')


def on_generate():
    if rolling:
        return
    sums_label.configure(text='Взлом мейнфрейма...')
    roll_key(generate_key())


def on_copy():
    key = key_entry.get()
    if not key or rolling:
        messagebox.showwarning('Пусто', 'Сначала сгенерируйте ключ!')
        return
    window.clipboard_clear()
    window.clipboard_append(key)
    messagebox.showinfo('Готово', 'Ключ скопирован в буфер обмена')


if __name__ == '__main__':
    window = tk.Tk()
    window.title('KEYGEN — вариант 4')
    window.geometry('640x400')
    window.resizable(False, False)

    bg_img = tk.PhotoImage(file=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bg_pic.png'))
    canvas = tk.Canvas(window, width=640, height=400, highlightthickness=0)
    canvas.place(x=0, y=0)
    canvas.create_image(0, 0, image=bg_img, anchor='nw')
    make_stars()

    frame = tk.Frame(window, bg='#1b1040', padx=20, pady=20)
    canvas.create_window(320, 200, window=frame)

    tk.Label(frame, text='GAME KEYGEN', font=('Courier', 26, 'bold'),
             bg='#1b1040', fg='#ffe66d').pack(pady=(0, 10))

    key_entry = tk.Entry(frame, font=('Courier', 24), justify='center',
                         width=16, state='readonly')
    key_entry.pack(pady=5)

    sums_label = tk.Label(frame, text='Нажмите «Сгенерировать»', font=('Courier', 11),
                          bg='#1b1040', fg='white')
    sums_label.pack(pady=5)

    btn_frame = tk.Frame(frame, bg='#1b1040')
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text='Сгенерировать', font=('Courier', 14, 'bold'),
              command=on_generate).pack(side='left', padx=5)
    tk.Button(btn_frame, text='Копировать', font=('Courier', 14),
              command=on_copy).pack(side='left', padx=5)
    music_btn = tk.Button(btn_frame, text='Музыка: вкл', font=('Courier', 14),
                          command=toggle_music)
    music_btn.pack(side='left', padx=5)
    tk.Button(btn_frame, text='Выход', font=('Courier', 14),
              command=on_exit).pack(side='left', padx=5)

    window.protocol('WM_DELETE_WINDOW', on_exit)
    start_music()
    animate()
    window.mainloop()
