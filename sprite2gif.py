from __future__ import print_function
from PIL import Image
import os.path
import subprocess
import shlex
import tempfile


def do_convert(png_fn, sprite_count, frame_duration=15, custom_order=None):
    sprite_images = []
    sprite_fds = []
    i1 = Image.open(png_fn)

    try:
        assert isinstance(i1, Image.Image)
        sprite_width = i1.size[0] / sprite_count
        sprite_height = i1.size[1]
        print(sprite_width, sprite_height)
        for x in range(0, sprite_count):
            crop_box = (x * sprite_width, 0, (x + 1) * sprite_width, sprite_height)
            print(crop_box)
            i2 = i1.crop(crop_box)
            sprite_fds.append(tempfile.NamedTemporaryFile(mode='wb', suffix='.png'))
            i2.save(sprite_fds[-1])
            sprite_fds[-1].flush()
            sprite_images.append(os.path.abspath(sprite_fds[-1].name))
            i2.close()
            # sprite_images.append(os.path.abspath(new_png_fn))

        if custom_order and isinstance(custom_order, list):
            new_sprite_list = []
            assert max(custom_order) < sprite_count
            for z in custom_order:
                new_sprite_list.append(sprite_images[z])
            sprite_images = new_sprite_list

        gif_fn = os.path.abspath(str(png_fn).rpartition('.')[0] + '__autogif.gif')
        im_args_str = "env convert -dispose 'previous' -delay {1} {0} -delay {1} -loop 0 '{2}'".format(
            " -delay {} ".format(str(frame_duration)).join(["\'" + fn + "\'" for fn in sprite_images]),
            str(frame_duration),
            gif_fn)

        im_args_list = shlex.split(im_args_str)
        print(im_args_list)
        print(im_args_str)
        p1 = subprocess.Popen(im_args_str, shell=True)
        p1.wait()
        print("done waiting")
        print(p1.returncode)

    finally:
        i1.close()
        for sfd in sprite_fds:
            sfd.close()


RYAN_SAMP = "/Users/ethan/Pictures/Ryan_capstone/samples/"
do_convert(RYAN_SAMP + "zombie_sprite_afro.png", 3, frame_duration=25, custom_order=[0, 1, 2, 1])
do_convert(RYAN_SAMP + "zombie_crowd_sprite.png", 2, 10)
do_convert(RYAN_SAMP + "hero_sprite.png", 4)
do_convert(RYAN_SAMP + "hero_sprite_armed_gag.png", 4)
do_convert(RYAN_SAMP + "hero_sprite_armed_gun.png", 4)
do_convert(RYAN_SAMP + "hero_sprite_armed_sword.png", 4)



