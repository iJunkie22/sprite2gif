from __future__ import print_function
from PIL import Image
import os.path
import subprocess
import shlex
import tempfile


class Sprite(object):
    def __init__(self, png_fn, frame_count=None, frame_width=None, order=None, frame_duration=15):
        self.sprite_image_fns = []
        self.sprite_image_fds = []
        self.source_fn = png_fn
        self.sprite_width = frame_width
        self.sprite_height = None
        self.source_frame_count = frame_count or 0
        assert frame_count or frame_width
        self.split_png(png_fn)
        if order:
            assert isinstance(order, list)
            assert max(order) < self.source_frame_count

        self.def_dur = frame_duration
        self.def_order = order or range(0, self.source_frame_count)

    def make_gif(self, frame_duration=None, outfile_fp="<AUTOMATIC>", order=None):
        frame_order = self.def_order
        frame_duration = frame_duration or self.def_dur

        if order and isinstance(order, list):
            assert max(order) < self.source_frame_count
            frame_order = order

        gif_sources = [self.sprite_image_fns[c] for c in frame_order]

        if outfile_fp == "<AUTOMATIC>":
            outfile_fp = os.path.abspath(str(self.source_fn).rpartition('.')[0] + '__autogif.gif')

        im_args_str = "env convert -dispose 'previous' -delay {1} {0} -delay {1} -loop 0 '{2}'".format(
            " -delay {} ".format(str(frame_duration)).join(["\'" + fn + "\'" for fn in gif_sources]),
            str(frame_duration),
            outfile_fp)

        p1 = subprocess.Popen(im_args_str, shell=True)
        p1.wait()
        return outfile_fp

    def split_png(self, png_fn):
        i1 = Image.open(png_fn)
        try:
            assert isinstance(i1, Image.Image)
            if self.source_frame_count == 0 and self.sprite_width:
                self.source_frame_count = i1.size[0] / self.sprite_width
            else:
                self.sprite_width = i1.size[0] / self.source_frame_count

            self.sprite_height = i1.size[1]
            print(self.sprite_width, self.sprite_height)
            for x in range(0, self.source_frame_count):
                crop_box = (x * self.sprite_width, 0, (x + 1) * self.sprite_width, self.sprite_height)
                print(crop_box)
                i2 = i1.crop(crop_box)
                self.sprite_image_fds.append(tempfile.NamedTemporaryFile(mode='wb', suffix='.png'))
                i2.save(self.sprite_image_fds[-1])
                self.sprite_image_fds[-1].flush()
                self.sprite_image_fns.append(os.path.abspath(self.sprite_image_fds[-1].name))
                i2.close()
        finally:
            i1.close()

    def close(self):
        for sfd in self.sprite_image_fds:
            sfd.close()

    def __del__(self):
        self.close()

    @classmethod
    def copy_conf(cls, sprite1, png_fn):
        assert isinstance(sprite1, Sprite)
        new_sprite = cls(png_fn,
                         frame_count=sprite1.source_frame_count,
                         frame_width=sprite1.sprite_width,
                         order=sprite1.def_order)
        return new_sprite

    def copy(self, png_fn):
        return self.__class__(png_fn,
                              frame_count=self.source_frame_count,
                              frame_width=self.sprite_width,
                              order=self.def_order)

    def regif(self, png_fn=None, png_fp=None):
        new_fp = png_fp or str(self.source_fn).rpartition('/')[0] + '/' + png_fn
        return self.copy(new_fp).make_gif()


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

# do_convert(RYAN_SAMP + "zombie_sprite_afro.png", 3, frame_duration=25, custom_order=[0, 1, 2, 1])
do_convert(RYAN_SAMP + "zombie_crowd_sprite.png", 2, 10)
# do_convert(RYAN_SAMP + "hero_sprite.png", 4)
# do_convert(RYAN_SAMP + "hero_sprite_armed_gag.png", 4)
# do_convert(RYAN_SAMP + "hero_sprite_armed_gun.png", 4)
# do_convert(RYAN_SAMP + "hero_sprite_armed_sword.png", 4)

s1 = Sprite(RYAN_SAMP + "zombie_sprite.png", 3, order=[0, 1, 2, 1], frame_duration=25)
s1.make_gif()
s1.regif("zombie_sprite_afro.png")

s2 = Sprite(RYAN_SAMP + "hero_sprite.png", frame_count=4)
s2.make_gif()
s2.regif("hero_sprite_armed_gag.png")
s2.regif("hero_sprite_armed_gun.png")
s2.regif("hero_sprite_armed_sword.png")

