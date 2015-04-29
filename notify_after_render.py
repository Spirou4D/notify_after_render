# <pep8-80 compliant>
# BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
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
# END GPL LICENSE BLOCK #####


bl_info = {
	"name": "Notify after Render",
	"description": "Use internet services to send you notifications at the end of render.",
	"author": "Spirou4D",
	"version": (1, 0),
	"blender": (2, 74, 0),
	"location": "Active buttons in properties > render panel",
	"warning": "Need the use of \"Auto save render\" add-ons absolutelly!",
	"wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Render/Notify_after_render",
	"category": "Render"}


import urllib, os, smtplib, bpy
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
# ------------------
from bpy.app.handlers import persistent
from bpy.props import StringProperty, FloatVectorProperty, BoolProperty
from bpy.path import basename
from bpy_extras.io_utils import ExportHelper
# -----------------
from re import findall
import pickle


def get_addon_preferences():
	#bpy.context.user_preferences.addons["notify_after_render"].preferences['sent_sms']=1
	#Par exemple:
	# addon_prefs = get_addon_preferences()
	# addon_prefs.url_smsservice
	addon_preferences = bpy.context.user_preferences.addons[__name__].preferences
	return addon_preferences

def get_filepath():
	blendname = basename(bpy.data.filepath).rpartition('.')[0]
	filepath = dirname(bpy.data.filepath) + SEP +'auto_saves'

	if not exists(filepath):
		mkdir(filepath)

	if bpy.context.scene.auto_save_subfolders:
		filepath = join(filepath, blendname)
		if not exists(filepath):
			mkdir(filepath)
	return filepath

def get_save_ID():
	blendname = basename(bpy.data.filepath).rpartition('.')[0]
	rndr = bpy.context.scene.render
	format = rndr.image_settings.file_format \
	= bpy.context.scene.auto_save_format
	if format == 'OPEN_EXR_MULTILAYER': extension = '.exr'
	if format == 'JPEG': extension = '.jpg'
	if format == 'PNG': extension = '.png'

	filepath = get_filepath()

	#imagefiles starting with the blendname
	files = [f for f in listdir(filepath) \
			if f.startswith(blendname) \
			and f.lower().endswith(('.png', '.jpg', '.jpeg', '.exr'))]

	highest = 0
	if files:
		for f in files:
			#find last numbers in the filename after the blendname
			suffix = findall('\d+', f.split(blendname)[-1])
			if suffix:
				if int(suffix[-1]) > highest:
					highest = int(suffix[-1])

	save_ID =  blendname + '_' + str(highest).zfill(3) + extension
	return save_ID

def NAR_custom_pref_save(context, filepath, WHOLE):
	addon_prefs = get_addon_preferences()

	if WHOLE == False:
		# /home/patrinux/Bureau/notify_after_render.nar
		FILEOUTPUT = "%s%s%s.nar" % (filepath.rpartition(SEP)[0],SEP,__name__)
	else:
		# /home/patrinux/Bureau/notify_after_render_prefs.nar
		FILEOUTPUT = "%s%s%s_%s" % (filepath.rpartition(SEP)[0],SEP,__name__,filepath.rpartition(SEP)[-1])
	PARAMS=dict()
	PARAMS['use_dropbow_service']=str(addon_prefs.use_dropbow_service)
	PARAMS['folderpath_dropbox']=str(addon_prefs.folderpath_dropbox)
	PARAMS['sent_sms']=str(addon_prefs.sent_sms)
	PARAMS['url_smsservice']=str(addon_prefs.url_smsservice)
	PARAMS['sent_mail']=str(addon_prefs.sent_mail)
	PARAMS['adress_mail']=str(addon_prefs.adress_mail)
	PARAMS['password_mail']=str(addon_prefs.password_mail)
	PARAMS['smtp_mail']=str(addon_prefs.smtp_mail)

	# Création du fichier .nar
	open(FILEOUTPUT,'wb')
	FILE=open(FILEOUTPUT,'wb')
	pickle.dump(PARAMS, FILE)

	# Fermeture de l'écriture
	FILE.close()

	return {'FINISHED'}

def NAR_custom_pref_load(context, filepath, WHOLE):
	addon_prefs = get_addon_preferences()

	# lecture du fichier .nar
	LOADFILE=open(filepath,'rb')
	PYRAW=pickle.load(LOADFILE)

	if len(PYRAW) == 8:
		if PYRAW["use_dropbow_service"]=="True":
			addon_prefs.use_dropbow_service=True
		else:
			addon_prefs.use_dropbow_service=False
		addon_prefs.folderpath_dropbox=PYRAW["folderpath_dropbox"]
		if PYRAW["sent_sms"]=="True":
			addon_prefs.sent_sms=True
		else:
			addon_prefs.sent_sms=False
		addon_prefs.url_smsservice=PYRAW["url_smsservice"]
		if PYRAW["sent_mail"]=="True":
			addon_prefs.sent_mail=True
		else:
			addon_prefs.sent_mail=False
		addon_prefs.adress_mail=PYRAW["adress_mail"]
		addon_prefs.password_mail=PYRAW["password_mail"]
		addon_prefs.smtp_mail=PYRAW["smtp_mail"]
	else:
		print('This file is not an official pref file.')
		return {'CANCELLED'}

	# Fermeture de la lecture
	LOADFILE.close()

	return {'FINISHED'}

class EXPORT_OT_preferences_save(bpy.types.Operator, ExportHelper):
	'''Only in the user prefs panel'''
	bl_idname = "export.preferences_export"
	bl_label = "Save"
	bl_description = "Save custom preferences in text file."

	filename_ext = ".nar"
	filter_glob = bpy.props.StringProperty(
			default="*.nar",
			options={'HIDDEN'},
			)
	use_setting = bpy.props.BoolProperty(
			name="With specification",
			description="Name automatically \"notify_after_render.nar\".",
			default=True,
			)

	def execute(self, context):
		return NAR_custom_pref_save(context, self.filepath, self.use_setting)


class IMPORT_OT_preferences_load(bpy.types.Operator, ExportHelper):
	'''Only in the user prefs panel'''
	bl_idname = "import_scene.preferences_load"
	bl_label = "Load"
	bl_description = "Load custom preference from text file."

	filename_ext = ".nar"
	filter_glob = bpy.props.StringProperty(
			default="*.nar",
			options={'HIDDEN'},
			)
	use_setting = bpy.props.BoolProperty(
			name="With specification",
			description="Name automatically \"notify_after_render.nar\".",
			default=True,
			)

	def execute(self, context):
		return NAR_custom_pref_load(context, self.filepath, self.use_setting)



class NAR_Addon_Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

# ---------------------DROPBOX
	use_dropbow_service  = BoolProperty(name="Use Dropbox",
								description="If you want to use a dropbow service:",
								default=False)

	folderpath_dropbox = bpy.props.StringProperty(
			description="Path to your dropbox 's folder:",
			name="Dropbox folder path",
			subtype='DIR_PATH',
			)

# ----------------------SMS
	sent_sms  = BoolProperty(name="Send SMS",
								description="If you want to send an informative sms:",
								default=False)

	url_smsservice = bpy.props.StringProperty(
			description="Preference of sms service",
			name="SMS sevice URL",
			subtype='PASSWORD',
			)

# ----------------------MAIL
	sent_mail  = BoolProperty(name="Send Mail",
								description="If you want to send an informative mail:",
								default=False)

	adress_mail = bpy.props.StringProperty(
			description="Test of the mail",
			name="Mail",
			default="tatata@blender.org",
			)

	password_mail = bpy.props.StringProperty(
			description="Test of the mail",
			name="Password",
			subtype='PASSWORD',
			)

	smtp_mail = bpy.props.StringProperty(
			description="Test of the mail",
			name="SMTP server",
			default="smtp.blender.org",
			)



	def draw(self, context):
		layout = self.layout

		split=layout.split(percentage=0.20)
		row = split.row()
		row.prop(self, "sent_sms")
		if self.sent_sms == True:
			row=split.row()
			row.prop(self, "url_smsservice")

		row = layout.row()
		row.prop(self, "sent_mail")
		if self.sent_mail == True:
			row = layout.row()
			row.prop(self, "adress_mail")
			row.prop(self, "password_mail")
			row.prop(self, "smtp_mail")

		split=layout.split(percentage=0.20)
		row = split.row()
		row.prop(self, "use_dropbow_service")
		if self.use_dropbow_service == True:
			row=split.row()
			row.prop(self, "folderpath_dropbox")

		box = layout.box()
		row=box.row()
		row.label("Custom preferences :")
		row.operator('import_scene.preferences_load', text='Load' )
		row.operator('export.preferences_export', text='Save' )




class RENDER_OT_copy_render_dropbox(bpy.types.Operator):
	#"""Copy render in you Dropbox""" >>bpy.ops.render.copy_render_dropbox()
	bl_idname = "render.copy_render_dropbox"
	bl_label = "Copy still render dropbox"
	bl_description = "Copy still render in your favorite Dropbox's folder."

	def execute(self, context):
		scene=context.scene
		addon_prefs = get_addon_preferences()
		A1 = addon_prefs.use_dropbow_service
		A2 = scene.save_after_render
		A3 = addon_prefs.folderpath_dropbox

		if not A1 or not A2 or A3=='' or not bpy.data.filepath:
			return
		rndr = scene.render
		original_format = rndr.image_settings.file_format

		save_ID = get_save_ID()
		copied_name = join(A3 , save_ID)

		image = bpy.data.images['Render Result']
		if not image:
			print('Dropbox_Save: Render Result not found. Image not copied')
			return

		try:
			 image.save_render(copied_name, scene=None)
			 print('Dropbox_Save:', copied_name)
		except:
			pass
		rndr.image_settings.file_format = original_format

		return {'FINISHED'}

	def invoke(self, context, event):
		try:
			execute(scene)
			print("Successfully render copied!")
		except:
			print("Error: unable to copy the render!")
		return {'FINISHED'}




class RENDER_OT_Sendmail(bpy.types.Operator):
	#"""Send Mail"""bpy.ops.render.notify_sendmail()
	bl_idname = "render.notify_sendmail"
	bl_label = "Send mail"
	bl_description = "Send a mail to notify you after a render."

	def execute(self, context):
		addon_prefs = get_addon_preferences()
		mFrom = addon_prefs.adress_mail
		passW = addon_prefs.password_mail
		smtpSer = addon_prefs.smtp_mail
		myRender = get_save_ID()

		if mFrom=='tatata@blender.org' \
		or passW=='' \
		or smtpSer=='smtp.blender.org':
			print('You must clearly setup your mail informations, please')
			return


		#Message contenant du text/plain
		Text = 'At :'+formatdate(localtime=True)+\
		', your render [ '+str(myRender) + ' ] is ready!'

		# Entêtes : from/to/subject
		msg = MIMEMultipart()
		msg['From'] = mFrom
		msg['To'] = mFrom
		msg['Date'] = formatdate(localtime=True)
		msg['Subject']="Blender has finished..."
		msg.attach(MIMEText(Text))

		# création d'un objet 'serveur'
		myserver = smtplib.SMTP(smtpSer, 587)
		myserver.ehlo()
		myserver.starttls()
		myserver.ehlo()
		myserver.login(mFrom, passW)

		# Envoie du mail
		myserver.sendmail(mFrom, mFrom, msg.as_string())
		myserver.quit()
		return {'FINISHED'}

	def invoke(self, context, event):
		try:
			execute(context)
			print("Successfully sent email")
		except SMTPException:
			print("Error: unable to send email")
		return {'FINISHED'}

def notifications_UI(self, context):
	addon_prefs = get_addon_preferences()
	layout = self.layout

	split=layout.split(percentage=0.33, align=True)
	row = split.row()
	row.label("Notification by:")
	row=split.row(align=True)
	row.prop(addon_prefs, 'sent_sms', text='SMS', toggle=False)
	row.prop(addon_prefs, 'sent_mail', text='Mail', toggle=False)
	row=split.row()
	row.prop(addon_prefs, 'use_dropbow_service', text='Use  Dropbox', toggle=False)

@persistent
def notifications_handler(scene):
	addon_prefs = get_addon_preferences()

	# DROPBOX
	A1 = addon_prefs.use_dropbow_service
	Dpath = addon_prefs.folderpath_dropbox
	# SMS
	A2 = addon_prefs.sent_sms
	myRender = get_save_ID()
	URL = addon_prefs.url_smsservice
	smsText = 'At :'+formatdate(localtime=True)+\
	', your render [ '+str(myRender) + ' ] is ready!'
	URL = URL +'&msg='+ urllib.parse.quote_plus(smsText)
	# MAIL
	A3 = addon_prefs.sent_mail

# ==========================================
	if   A1 and Dpath=='':
		print('You must choose a dropbox folder in user preferences, please!')
	elif A1 and not Dpath=='':
		bpy.ops.render.copy_render_dropbox()
	else:
		print('No render copied in dropbox!')

	if   A2 and URL=='':
		print('You must setup the url of your sms service, please!')
	elif A2 and not URL=='':
		x = urllib.request.urlopen(URL)
	else:
		print('No SMS sent!')

	if A3:
		bpy.ops.render.notify_sendmail()
	else:
		print('No MAIL sent!')



def register():
	bpy.utils.register_module(__name__)
	bpy.app.handlers.render_post.append(notifications_handler)
	bpy.types.RENDER_PT_render.append(notifications_UI)


def unregister():
	bpy.types.RENDER_PT_render.remove(notifications_UI)
	bpy.app.handlers.render_post.remove(notifications_handler)
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
