# <pep8-80 compliant>
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name":        "Notify after Render",
    "description": "Use internet services to send you notifications at the end of render.",
    "author":      "Spirou4D",
    "version":     (1, 3, 0),
    "blender":     (2, 80, 0),
    "location":    "Active buttons in properties > render panel",
    "warning":     "Need the use of \"Auto save render\" add-ons absolutely!",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Render/Notify_after_render",
    "tracker_url": "https://github.com/Spirou4D/Notify-after-render/issues",
    "category":    "Render"
    }

import bpy
from bpy.app.handlers import persistent
from bpy.types import Operator, AddonPreferences, Panel
from bpy.props import IntProperty, StringProperty, BoolProperty
from bpy.path import basename
from bpy_extras.io_utils import ExportHelper

# add-on modules import, all setup in this file
# ------------------
import urllib, os, smtplib, email.utils, getpass
# ------------------
import urllib.request
from urllib.parse import urlencode
# ------------------
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
# ------------------
from os.path import dirname, exists, join
from os import mkdir, listdir
SEP = os.sep
# -----------------
from re import findall
import pickle

# updater ops import, all setup in this file
from . import addon_updater_ops

bpy.types.Scene.use_notifications= bpy.props.BoolProperty(
        name=" Use Notifications",
        description="If enabled, notify with modes",
        default=False,
        options={'HIDDEN'},
        )

def get_addon_preferences():
    # bpy.context.preferences.addons["notify_after_render"].preferences['send_sms']=1
    # Par exemple:
    # addon_prefs = get_addon_preferences()
    # addon_prefs.url_smsservice
    addon_preferences = bpy.context.preferences.addons[__package__].preferences
    return addon_preferences

def get_filepath():
    blendname = basename(bpy.data.filepath).rpartition('.')[0]
    filepath = dirname(bpy.data.filepath) + SEP + 'auto_saves'

    if not exists(filepath):
        mkdir(filepath)

    if bpy.context.scene.auto_save_subfolders:
        filepath = join(filepath, blendname)
        if not exists(filepath):
            mkdir(filepath)
    return filepath

def get_save_ID():
    rdff = bpy.context.scene.render.image_settings.file_format
    blendname = basename(bpy.data.filepath).rpartition('.')[0]
    formats=['BMP', 'IRIS', 'PNG', 'JPEG', 'JPEG2000', 'TARGA', 'TARGA_RAW', \
    'CINEON', 'DPX', 'OPEN_EXR_MULTILAYER', 'OPEN_EXR', 'HDR', 'TIFF', \
    'AVI_JPEG', 'AVI_RAW', 'FFMPEG']
    exts=['.bmp', '.rgb', '.png', '.jpg', '.jp2', '.tga', '.tga', '.cin', \
    '.exr', '.exr', '.hdr', '.tiff', '.avi', '.avi', '.ffmpeg']


    format = bpy.context.scene.auto_save_format
    if format not in formats : format = rdff
    i=0
    while i < len(formats):
        if formats[i]==format : extension = exts[i]
        i += 1

    filepath = get_filepath()

    # imagefiles starting with the blendname
    files = [f for f in listdir(filepath)  \
             if f.startswith(blendname)  \
             and f.lower().endswith(('.png', '.jpg', '.jpeg', '.exr'))]

    highest = 0
    if files:
        for f in files:
            # find last numbers in the filename after the blendname
            suffix = findall('\d+', f.split(blendname)[-1])
            if suffix:
                if int(suffix[-1]) > highest:
                    highest = int(suffix[-1])

    save_ID = blendname + '_' + str(highest).zfill(3) + extension
    return save_ID

def NAR_custom_pref_save(context, filepath, WHOLE):
    addon_prefs = get_addon_preferences()

    if WHOLE == False:
        # /home/patrinux/Bureau/notify_after_render.nar
        FILEOUTPUT = "%s%s%s.nar" % (filepath.rpartition(SEP)[0], SEP, __name__)
    else:
        # /home/patrinux/Bureau/notify_after_render_prefs.nar
        FILEOUTPUT = "%s%s%s_%s" % (filepath.rpartition(SEP)[0], SEP, __name__, filepath.rpartition(SEP)[-1])
    PARAMS = dict()
    PARAMS['use_dropbow_service'] = str(addon_prefs.use_dropbow_service)
    PARAMS['folderpath_dropbox'] = str(addon_prefs.folderpath_dropbox)
    PARAMS['send_mail'] = str(addon_prefs.send_mail)
    PARAMS['adress_mail'] = str(addon_prefs.adress_mail)
    PARAMS['password_mail'] = str(addon_prefs.password_mail)
    PARAMS['smtp_mail'] = str(addon_prefs.smtp_mail)
    PARAMS['send_sms'] = str(addon_prefs.send_sms)
    PARAMS['url_smsservice'] = str(addon_prefs.url_smsservice)

    # Création du fichier .nar
    open(FILEOUTPUT, 'wb')
    FILE = open(FILEOUTPUT, 'wb')
    pickle.dump(PARAMS, FILE)

    # Fermeture de l'écriture
    FILE.close()

    return {'FINISHED'}

def NAR_custom_pref_load(context, filepath, WHOLE):
    addon_prefs = get_addon_preferences()

    # lecture du fichier .nar
    LOADFILE = open(filepath, 'rb')
    PYRAW = pickle.load(LOADFILE)

    if len(PYRAW) == 8:
        if PYRAW["use_dropbow_service"] == "True":
            addon_prefs.use_dropbow_service = True
        else:
            addon_prefs.use_dropbow_service = False
        addon_prefs.folderpath_dropbox = PYRAW["folderpath_dropbox"]
        if PYRAW["send_mail"] == "True":
            addon_prefs.send_mail = True
        else:
            addon_prefs.send_mail = False
        addon_prefs.adress_mail = PYRAW["adress_mail"]
        addon_prefs.password_mail = PYRAW["password_mail"]
        addon_prefs.smtp_mail = PYRAW["smtp_mail"]
        if PYRAW["send_sms"] == "True":
            addon_prefs.send_sms = True
        else:
            addon_prefs.send_sms = False
        addon_prefs.url_smsservice = PYRAW["url_smsservice"]
    else:
        print("This file isn\'t an official .nar pref file.")
        return {'CANCELLED'}

    # Fermeture de la lecture
    LOADFILE.close()

    return {'FINISHED'}


@persistent
def notifications_handler(scene):
    addon_prefs = get_addon_preferences()

    # SMS
    A1 = addon_prefs.send_sms
    myRender = get_save_ID()
    smsText = 'At :' + formatdate(localtime=True) + \
              ', your render [ ' + str(myRender) + ' ] is ready!'
    URL = addon_prefs.url_smsservice
    URL = URL + '&msg=' + urllib.parse.quote_plus(smsText)

    # MAIL
    A2 = addon_prefs.send_mail

    # DROPBOX
    A3 = addon_prefs.use_dropbow_service
    Dpath = addon_prefs.folderpath_dropbox

    # ==========================================
    if A1 and URL == '':
        print('You must setup the url of your sms service, please!')
    elif A1 and not URL == '':
        smsx = urllib.request.urlopen(URL, data=None)
    else:
        print('No SMS sent!')

    if A2:
        bpy.ops.render.notify_sendmail()
    else:
        print('No mail sent!')

    if A3 and Dpath == '':
        print('You must choose a dropbox folder in user preferences, please!')
    elif A3 and not Dpath == '':
        bpy.ops.render.copy_render_dropbox()
    else:
        print('No render copied in dropbox!')


class EXPORT_OT_preferences_save(Operator, ExportHelper):
    '''Only in the user prefs panel'''
    bl_idname = "export.preferences_export"
    bl_label = "Save"
    bl_description = "Save custom preferences in text file."

    filename_ext = ".nar"
    filter_glob : StringProperty(
        default="*.nar",
        options={'HIDDEN'},
        )
    use_setting : BoolProperty(
        name="With specification",
        description="Name automatically \"notify_after_render.nar\".",
        default=True,
        )

    def execute(self, context):
        return NAR_custom_pref_save(context, self.filepath, self.use_setting)


class IMPORT_OT_preferences_load(Operator, ExportHelper):
    '''Only in the user prefs panel'''
    bl_idname = "import.preferences_load"
    bl_label = "Load"
    bl_description = "Load custom preference from text file."

    filename_ext = ".nar"
    filter_glob : StringProperty(
        default="*.nar",
        options={'HIDDEN'},
        )
    use_setting : BoolProperty(
        name="With specification",
        description="Name automatically \"notify_after_render.nar\".",
        default=True,
        )

    def execute(self, context):
        return NAR_custom_pref_load(context, self.filepath, self.use_setting)


class RENDER_OT_copy_render_dropbox(Operator):
    """Copy render in you Dropbox"""
    # bpy.ops.render.copy_render_dropbox()
    bl_idname = "render.copy_render_dropbox"
    bl_label = "Copy still render dropbox"
    bl_description = "Copy still render in your favorite Dropbox's folder."

    def execute(self, context):
        scene = context.scene
        addon_prefs = get_addon_preferences()
        A1 = addon_prefs.use_dropbow_service
        A2 = scene.auto_save_after_render
        A3 = addon_prefs.folderpath_dropbox

        if not A1 or not A2 or A3 == '' or bpy.data.filepath =='':
            return {'FINISHED'} 
        rndr = scene.render
        original_format = rndr.image_settings.file_format

        save_ID = get_save_ID()
        copied_name = join(A3, save_ID)

        image = bpy.data.images['Render Result']
        if not image:
            print('Dropbox_Save: Render Result not found. Image not copied')
            return {'FINISHED'} 

        try:
            image.save_render(copied_name, scene=None)
            print('Dropbox_Save:', copied_name)
        except:
            pass
        rndr.image_settings.file_format = original_format

        return  {'FINISHED'} 

    def invoke(self, context, event):
        try:
            execute(scene)
            print("Successfully render copied!")
        except:
            print("Error: unable to copy the render!")
        return {'FINISHED'}


class RENDER_OT_notify_sendmail(Operator):
    """Send Mail"""
    # bpy.ops.render.notify_sendmail()
    bl_idname = "render.notify_sendmail"
    bl_label = "Send mail"
    bl_description = "Send a mail to notify you after a render."

    def execute(self, context):
        addon_prefs = get_addon_preferences()
        mFrom = addon_prefs.adress_mail
        passW = addon_prefs.password_mail
        smtpSer = addon_prefs.smtp_mail
        myRender = get_save_ID()

        if mFrom == 'tatata@blender.org' or smtpSer == 'smtp.blender.org':
            print('You must clearly setup your mail informations, please!')
            return {'FINISHED'} 

        # Message contenant du text/plain
        Text = 'At :' + formatdate(localtime=True) + \
               ', your render [ ' + str(myRender) + ' ] is ready!'

        # Entêtes : from/to/subject
        msg = MIMEMultipart()
        msg['From'] =  email.utils.formataddr(('Author', mFrom))
        msg['To'] = email.utils.formataddr(('Recipient', mFrom))
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "Blender has finished..."
        msg.attach(MIMEText(Text))

        # création d'un objet 'serveur'
        myserver = smtplib.SMTP(smtpSer, 587) # raw 25 or SSL/TLS 465 or raw 587
        try:
            myserver.set_debuglevel(True)

            # identify ourselves, prompting server for supported features
            myserver.ehlo()

            # If we can encrypt this session, do it
            if myserver.has_extn('STARTTLS'):
                myserver.starttls()
                myserver.ehlo() # re-identify ourselves over TLS connection
            myserver.login(mFrom, passW)

            # Envoie du mail
            myserver.sendmail(mFrom, [mFrom], msg.as_string())

        finally:
            myserver.quit()
        return {'FINISHED'}


    def invoke(self, context, event):
        try:
            execute(context)
            print("Successfully sent email")
        except Exception as err:
            print('Unable to send email: Not found -> ', err)
        return {'FINISHED'}


class RENDER_PT_notifications(Panel):
    bl_label = "Notify Renders with..."
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_parent_id = "RENDER_PT_context"
    bl_options = {'DEFAULT_CLOSED'}
    
    
        
    def draw_header(self, context):
        props = context.scene
        self.layout.prop(props, "use_notifications", text="")
        
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        addon_prefs = get_addon_preferences()
        
        props = context.scene
        layout.active = props.use_notifications  
        col= layout.column()
        col.prop(addon_prefs, 'send_sms', text='SMS', toggle=False)
        col.prop(addon_prefs, 'send_mail', text='Mail', toggle=False)
        col.prop(addon_prefs, 'use_dropbow_service', text='Use Dropbox', toggle=False)


class OBJECT_PT_UpdaterPanel(Panel):
    """Panel to demo popup notice and ignoring functionality"""
    bl_label = "Notify after render"
    bl_idname = "OBJECT_PT_UpdaterPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        layout = self.layout

        # Call to check for update in background
        # note: built-in checks ensure it runs at most once
        # and will run in the background thread, not blocking
        # or hanging blender
        # Internally also checks to see if auto-check enabled
        # and if the time interval has passed
        addon_updater_ops.check_for_update_background()


        layout.label(text="Notify after render Update")
        layout.label(text="")

        col = layout.column()
        col.scale_y = 0.7
        col.label(text="If an update is ready,")
        col.label(text="popup triggered by opening")
        col.label(text="this panel, plus a box ui")

        # could also use your own custom drawing
        # based on shared variables
        if addon_updater_ops.updater.update_ready == True:
            layout.label(text="Custom update message", icon="INFO")
        layout.label(text="")

        # call built-in function with draw code/checks
        addon_updater_ops.update_notice_box_ui(self, context)


# add-on preferences
class NAR_Preferences(AddonPreferences):
    bl_idname = __package__

    # addon updater preferences
    auto_check_update : BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False,
        )
    updater_intrval_months : IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
        )
    updater_intrval_days : IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31
        )
    updater_intrval_hours : IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes : IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )

    # ---------------------DROPBOX
    use_dropbow_service : BoolProperty(
        name="Use Dropbox",
        description="If you want to use a dropbox service:",
        default=False,
        )

    folderpath_dropbox : StringProperty(
        description="Path to your dropbox 's folder:",
        name="Dropbox folder path",
        subtype='DIR_PATH',
        )

    # ----------------------SMS
    send_sms : BoolProperty(
        name="Send SMS",
        description="If you want to send an informative sms:",
        default=False,
        )

    url_smsservice : StringProperty(
        description="Preference of sms service",
        name="SMS sevice URL",
        subtype='PASSWORD',
        )

    # ----------------------MAIL
    send_mail : BoolProperty(
        name="Send Mail",
        description="If you want to send an informative mail:",
        default=False,
        )

    adress_mail : StringProperty(
        description="Test of the mail",
        name="Mail",
        default="tatata@blender.org",
        )

    password_mail : StringProperty(
        description="Test of the mail",
        name="Password",
        subtype='PASSWORD',
        )

    smtp_mail : StringProperty(
        description="Test of the mail",
        name="SMTP server",
        default="smtp.blender.org",
        )

    def draw(self, context):
        layout = self.layout
        mainrow = layout.row()

        col = mainrow.column()
        split = col.split(factor=0.20)
        row = split.row()
        row.prop(self, "send_sms")
        if self.send_sms == True:
            row = split.row()
            row.prop(self, "url_smsservice")

        split = col.split(factor=0.20)
        row = col.row()
        row.prop(self, "send_mail")
        if self.send_mail == True:
            row = col.row()
            row.prop(self, "adress_mail")
            row.prop(self, "password_mail")
            row.prop(self, "smtp_mail")

        split = col.split(factor=0.20)
        row = split.row()
        row.prop(self, "use_dropbow_service")
        if self.use_dropbow_service == True:
            row = split.row()
            row.prop(self, "folderpath_dropbox")

        box = col.box()
        row = box.row()
        row.label(text="Custom preferences :")
        row.operator('import.preferences_load', text='Load')
        row.operator('export.preferences_export', text='Save')

        # -----------------------------------------------------------------UPDATER
        # col = layout.column() # works best if a column, or even just self.layout
        col = mainrow.column()

        # updater draw function
        # could also pass in col as third arg
        addon_updater_ops.update_settings_ui(self, context)

        # Alternate draw function, which is more condensed and can be
        # placed within an existing draw function. Only contains:
        #   1) check for update/update now buttons
        #   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

        # Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # col.operator("wm.url_open","Open webpage ").url=addon_updater_ops.updater.website

classes = (       
        EXPORT_OT_preferences_save,
        IMPORT_OT_preferences_load,
        RENDER_OT_copy_render_dropbox,
        RENDER_OT_notify_sendmail,
        RENDER_PT_notifications,
        OBJECT_PT_UpdaterPanel,
        NAR_Preferences
    )


def register():
    # addon updater code and configurations
    # in case of broken version, try to register the updater first
    # so that users can revert back to a working version
    #addon_updater_ops.register(bl_info)

    # register classes
    from bpy.utils import register_class
    for cls in classes:
        addon_updater_ops.make_annotations(OBJECT_PT_UpdaterPanel) # to avoid blender 2.8 warnings
        bpy.utils.register_class(cls)
    bpy.types.RENDER_PT_context.append(RENDER_PT_notifications)
    bpy.app.handlers.render_post.append(notifications_handler)



def unregister():
    bpy.types.RENDER_PT_context.remove(RENDER_PT_notifications)
    bpy.app.handlers.render_post.remove(notifications_handler)
    from bpy.utils import register_class
    # addon updater unregister
    #addon_updater_ops.unregister()
    # register classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
