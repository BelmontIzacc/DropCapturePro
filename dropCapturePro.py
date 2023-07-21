import subprocess
import sys

def check_install(package):
    try:
        subprocess.check_output([sys.executable, '-m', 'pip', 'show', package])
        print(f"{package} está instalado.")
    except subprocess.CalledProcessError:
        print(f"{package} no está instalado. Instalando...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Lista de paquetes a verificar e instalar
packages = ['kivy', 'opencv-python', 'kivymd', 'numpy']

# Verificar e instalar paquetes
for package in packages:
    check_install(package)

# import kivy dependencies
# from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton
from kivy.uix.label import Label

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown

# import kivy UX components
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.config import Config
from kivy.uix.actionbar import ActionBar
from kivy.uix.actionbar import ActionView
from kivy.uix.actionbar import ActionPrevious

# import other kivy stuff
from kivy.clock import Clock
from kivy.graphics.texture import Texture

# import other dependencies
import cv2
from tkinter import Tk, messagebox
import datetime
import numpy as np

Config.set('graphics', 'width', 1200)
Config.set('graphics', 'height', 700)

# Build app and layout
class CamApp(MDApp):

    def build(self):   
        # valores por defecto     
        self.fps = 30
        self.cam1 = 9
        self.cam2 = 9
        self.start_captureCAM1()
        self.start_captureCAM2()
        self.scoreCam1 = 0
        self.scoreCam2 = 0

        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day

        self.toDay = str(year)+"_"+str(month)+"_"+str(day)
        
        self.segCAM1 = -1
        self.segCAM2 = -1

        self.rotatedCam1 = 0
        self.rotatedCam2 = 0

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepOrange"

        # Top - Menu superior
        C_Top = BoxLayout(orientation = 'vertical', size_hint=(1,.12))
        menulayout = GridLayout(cols=1)

        # Crear Action Bar
        action_bar = ActionBar()
        action_view = ActionView()
        action_bar.add_widget(action_view)

        # Crear botón previo en Action Bar
        action_prev = ActionPrevious(with_previous=False, title='DropCapturePro')
        action_view.add_widget(action_prev)

        # Crear submenú para seleccionar cámara
        camera_dropdown = DropDown()

        # Crear elementos del menú el numero de camara a elegir
        # son dos camaras que se pueden ver y se puede elegir de la camara 0 a la 2, 0 = integrada, 1 = USB1, 2 = USB2
        item1 = GridLayout(cols=1, size_hint_y=None, height=40)
        item1_button = Button(text='CAM 1', size_hint_y=None, height=40)
        item1_dropdown = DropDown()
        item1_button.bind(on_release=item1_dropdown.open)
        item1.add_widget(item1_button)
        item1_dropdown.bind(on_select=lambda instance, x: self.close_dropdown(item1_dropdown))
        button1_item1 = Button(text=' Camera 1', size_hint_y=None, height=44)
        button1_item1.bind(on_release=lambda btn: self.set_camera1(0, button1_item1, item1_dropdown))
        button2_item1 = Button(text=' Camera 2', size_hint_y=None, height=44)
        button2_item1.bind(on_release=lambda btn: self.set_camera1(1, button2_item1, item1_dropdown))
        button3_item1 = Button(text=' Camera 3', size_hint_y=None, height=44)
        button3_item1.bind(on_release=lambda btn: self.set_camera1(2, button2_item1, item1_dropdown))
        item1_dropdown.add_widget(button1_item1)
        item1_dropdown.add_widget(button2_item1)
        item1_dropdown.add_widget(button3_item1)

        item2 = GridLayout(cols=1, size_hint_y=None, height=40)
        item2_button = Button(text='CAM 2', size_hint_y=None, height=40)
        item2_dropdown = DropDown()
        item2_button.bind(on_release=item2_dropdown.open)
        item2.add_widget(item2_button)
        item2_dropdown.bind(on_select=lambda instance, x: self.close_dropdown(item2_dropdown))
        button1_item2 = Button(text=' Camera 1', size_hint_y=None, height=44)
        button1_item2.bind(on_release=lambda btn: self.set_camera2(0, item2_button, item2_dropdown))
        button2_item2 = Button(text=' Camera 2', size_hint_y=None, height=44)
        button2_item2.bind(on_release=lambda btn: self.set_camera2(1, item2_button, item2_dropdown))
        button3_item2 = Button(text=' Camera 3', size_hint_y=None, height=44)
        button3_item2.bind(on_release=lambda btn: self.set_camera2(2, item2_button, item2_dropdown))
        item2_dropdown.add_widget(button1_item2)
        item2_dropdown.add_widget(button2_item2)
        item2_dropdown.add_widget(button3_item2)

        # Crear elementos del menu para indicar a cuantos fps a modificar
        itemMeta1 = GridLayout(cols=1, size_hint_y=None, height=40)
        item1_itemMeta1button = Button(text='FPS', size_hint_y=None, height=40)
        item1_Metadropdown = DropDown()
        item1_itemMeta1button.bind(on_release=item1_Metadropdown.open)
        itemMeta1.add_widget(item1_itemMeta1button)
        item1_Metadropdown.bind(on_select=lambda instance, x: self.close_dropdown(item1_Metadropdown))
        button0_Metaitem1 = Button(text=' 15', size_hint_y=None, height=44)
        button0_Metaitem1.bind(on_release=lambda btn: self.set_FPS(15, item1_Metadropdown))
        button1_Metaitem1 = Button(text=' 25', size_hint_y=None, height=44)
        button1_Metaitem1.bind(on_release=lambda btn: self.set_FPS(25, item1_Metadropdown))
        button2_Metaitem1 = Button(text=' 30', size_hint_y=None, height=44)
        button2_Metaitem1.bind(on_release=lambda btn: self.set_FPS(30, item1_Metadropdown))
        button3_Metaitem1 = Button(text=' 60', size_hint_y=None, height=44)
        button3_Metaitem1.bind(on_release=lambda btn: self.set_FPS(60, item1_Metadropdown))
        item1_Metadropdown.add_widget(button0_Metaitem1)
        item1_Metadropdown.add_widget(button1_Metaitem1)
        item1_Metadropdown.add_widget(button2_Metaitem1)
        item1_Metadropdown.add_widget(button3_Metaitem1)

        # Agregar elementos al menú desplegable de la camara
        camera_dropdown.add_widget(itemMeta1)
        camera_dropdown.add_widget(item1)
        camera_dropdown.add_widget(item2)

        # Crear botón de selección de cámara
        camera_button = Button(text='Camera', size_hint=(.1, 1))
        camera_button.bind(on_release=camera_dropdown.open)

        # Crear submenú para seleccionar cámara
        meta_dropdown = DropDown()

        # Crear elementos del menu para indicar datos del video
        button2 = Button(text='Data Video', size_hint_y=None, height=44)
        button2.bind(on_release=lambda btn: self.close_dropdown(meta_dropdown))
        
        # Crear elementos del menu para indicar medidas del video
        button3 = Button(text='Computer Vision', size_hint_y=None, height=44)
        button3.bind(on_release=lambda btn: self.close_dropdown(meta_dropdown))

        # Agregar elementos al menú desplegable de MetaDatos
        meta_dropdown.add_widget(button2)
        meta_dropdown.add_widget(button3)

        # Crear botón para metadata mostrar distancia en tiempo real y datos del video
        meta_button = Button(text='Metadata', size_hint=(.1, 1))
        meta_button.bind(on_release=meta_dropdown.open)

        # Agregar al layout del menu la barra y el boton para la camara
        menuOptions = BoxLayout(orientation='horizontal')
        menuOptions.add_widget(camera_button)
        menuOptions.add_widget(meta_button)

        menulayout.add_widget(action_bar)
        menulayout.add_widget(menuOptions)

        # Agrega barra de menu
        self.menuLayout = menulayout
        C_Top.add_widget(self.menuLayout)
        self.top = C_Top

        # espacio de las imagenes
        self.web_cam1 = Image(size_hint=(.40, 1))
        self.web_cam2 = Image(size_hint=(.40, 1))
        
        
        C_OptionsPlayCAM1 = BoxLayout(orientation = 'horizontal', size_hint=(1, 1))

        C_PLayCam1 = BoxLayout(orientation = 'vertical', size_hint=(1, 1))
        
        labelPlay = Label(text="CAM 1", size_hint=(None, None), font_size=20, pos_hint={"center_x": 0.5, "y": 0})  # Alineación vertical inferior)
        
        ini_cam1 = MDFloatingActionButton(text="PLAY C1",
                                          size_hint=(None, None), 
                                          icon="img/play.png", 
                                          halign= "center",
                                          type="large",  # Posición del botón en el centro
                                          md_bg_color="#fefbff",
                                          pos_hint={"center_x": 0.5, "center_y": 0.5},
                                          icon_color="#311021")
        ini_cam1.bind(on_release=self.playVideoCam1)

        C_PLayCam1.add_widget(ini_cam1)
        C_PLayCam1.add_widget(labelPlay)

        C_StopCam1 = BoxLayout(orientation = 'vertical', size_hint=(1, 1))

        labelStop = Label(text="CAM 1", size_hint=(None, None), font_size=20, pos_hint={"center_x": 0.5, "y": 0})  # Alineación vertical inferior)
        
        ini_cam1Stop = MDFloatingActionButton(text="STOP C1",
                                          size_hint=(None, None), 
                                          icon="img/stop.png", 
                                          halign= "center",
                                          type="large",  # Posición del botón en el centro
                                          md_bg_color="#fefbff",
                                          pos_hint={"center_x": 0.5, "center_y": 0.5},
                                          icon_color="#311021")
        ini_cam1Stop.bind(on_release=self.stopVideoCam1)
 
        C_StopCam1.add_widget(ini_cam1Stop)
        C_StopCam1.add_widget(labelStop)

        C_OptionsPlayCAM1.add_widget(C_PLayCam1)
        C_OptionsPlayCAM1.add_widget(C_StopCam1)
        
        C_OptionsPlayCAM2 = BoxLayout(orientation = 'horizontal', size_hint=(1, 1))

        C_PLayCam2 = BoxLayout(orientation = 'vertical', size_hint=(1, 1))
        
        labelPlayCAM2 = Label(text="CAM 2", size_hint=(None, None), font_size=20, pos_hint={"center_x": 0.5, "y": 0})  # Alineación vertical inferior)
        
        ini_cam2 = MDFloatingActionButton(text="PLAY C1",
                                          size_hint=(None, None), 
                                          icon="img/play.png", 
                                          halign= "center",
                                          type="large",  # Posición del botón en el centro
                                          md_bg_color="#fefbff",
                                          pos_hint={"center_x": 0.5, "center_y": 0.5},
                                          icon_color="#311021")
        ini_cam2.bind(on_release=self.playVideoCam2)

        C_PLayCam2.add_widget(ini_cam2)
        C_PLayCam2.add_widget(labelPlayCAM2)

        C_StopCam2 = BoxLayout(orientation = 'vertical', size_hint=(1, 1))

        labelStopCAM2 = Label(text="CAM 2", size_hint=(None, None), font_size=20, pos_hint={"center_x": 0.5, "y": 0})  # Alineación vertical inferior)
        
        ini_cam2Stop = MDFloatingActionButton(text="STOP C1",
                                          size_hint=(None, None), 
                                          icon="img/stop.png", 
                                          halign= "center",
                                          type="large",  # Posición del botón en el centro
                                          md_bg_color="#fefbff",
                                          pos_hint={"center_x": 0.5, "center_y": 0.5},
                                          icon_color="#311021")
        ini_cam2Stop.bind(on_release=self.stopVideoCam2)

        C_StopCam2.add_widget(ini_cam2Stop)
        C_StopCam2.add_widget(labelStopCAM2)

        C_OptionsPlayCAM2.add_widget(C_PLayCam2)
        C_OptionsPlayCAM2.add_widget(C_StopCam2)       
        

        # rotate_imageCAM1

        C_OptionsRotate = BoxLayout(orientation = 'horizontal', size_hint=(1, 1))

        C_rotateCam1 = BoxLayout(orientation = 'vertical', size_hint=(1, 1))
        
        labelrotateCAM1 = Label(text="CAM 1", size_hint=(None, None), font_size=20, pos_hint={"center_x": 0.5, "y": 0})  # Alineación vertical inferior)
        
        rot_cam1 = MDFloatingActionButton(text="PLAY C1",
                                          size_hint=(None, None), 
                                          icon="img/right.png", 
                                          halign= "center",
                                          type="large",  # Posición del botón en el centro
                                          md_bg_color="#fefbff",
                                          pos_hint={"center_x": 0.5, "center_y": 0.5},
                                          icon_color="#311021")
        rot_cam1.bind(on_release=self.rotate_imageCAM1)

        C_rotateCam1.add_widget(rot_cam1)
        C_rotateCam1.add_widget(labelrotateCAM1)

        C_rotateCam2 = BoxLayout(orientation = 'vertical', size_hint=(1, 1))

        labelrotateCAM2 = Label(text="CAM 2", size_hint=(None, None), font_size=20, pos_hint={"center_x": 0.5, "y": 0})  # Alineación vertical inferior)
        
        rot_cam2 = MDFloatingActionButton(text="STOP C1",
                                          size_hint=(None, None), 
                                          icon="img/right.png", 
                                          halign= "center",
                                          type="large",  # Posición del botón en el centro
                                          md_bg_color="#fefbff",
                                          pos_hint={"center_x": 0.5, "center_y": 0.5},
                                          icon_color="#311021")
        rot_cam2.bind(on_release=self.rotate_imageCAM2)

        C_rotateCam2.add_widget(rot_cam2)
        C_rotateCam2.add_widget(labelrotateCAM2)

        C_OptionsRotate.add_widget(C_rotateCam1)
        C_OptionsRotate.add_widget(C_rotateCam2)

        # control de tamaño del panel de botones de opciones
        C_Options = BoxLayout(orientation = 'vertical', size_hint=(.2,1))

        C_Options.add_widget(C_OptionsPlayCAM1)
        C_Options.add_widget(C_OptionsPlayCAM2)
        C_Options.add_widget(C_OptionsRotate)

        self.Options = C_Options
        
        # Body - Apartado de los videos
        C_Body = BoxLayout(orientation = 'horizontal', size_hint=(1,.85))
        
        C_Body.add_widget(self.web_cam1)
        C_Body.add_widget(self.web_cam2)
        C_Body.add_widget(self.Options)

        self.body = C_Body

        C_Bottom = BoxLayout(orientation = 'horizontal', size_hint=(1, .03))

        C_BottomCAM1 = BoxLayout(orientation = 'vertical', size_hint=(1, 1), spacing=12, pos_hint={"y": -1})
        text1Cam1 = Label(text="CAM 1", size_hint=(None, 1), font_size=15, )

        C_BottomCAM1.add_widget(text1Cam1)

        C_BottomCAM2 = BoxLayout(orientation = 'vertical', size_hint=(1, 1), spacing=12, pos_hint={"y": -1})
        text1Cam2 = Label(text="CAM 2", size_hint=(None, 1), font_size=15,)

        C_BottomCAM2.add_widget(text1Cam2)

        C_Bottom.add_widget(C_BottomCAM1)
        C_Bottom.add_widget(C_BottomCAM2)
        
        # spacing=10
        self.bottom = C_Bottom

        # Acomodo general de los elementos de la vista (Top, body)
        layoutMain = BoxLayout(orientation = 'vertical')
        layoutMain.add_widget(self.top)
        layoutMain.add_widget(self.bottom)
        layoutMain.add_widget(self.body)

        return layoutMain

    def playVideoCam1(self, args):
        if self.scoreCam1 == 0:
            self.scoreCam1 = 1

            now = datetime.datetime.now()
            hour = now.hour
            minute = now.minute
            second = now.second

            nameVideoCam1 = self.toDay+'_'+str(hour)+'.'+str(minute)+'.'+str(second)+'_CAM1.avi'

            self.outCam1 = cv2.VideoWriter(nameVideoCam1, cv2.VideoWriter_fourcc('M','J','P','G'), self.fps, (640, 480))
            print("Record video CAM1 On")
            messagebox.showinfo('Iniciando', 'Iniciando grabación de la CAM1')
        else:
            messagebox.showinfo('Aviso!','Grabación de la CAM1 en proceso...')
    
    def playVideoCam2(self, args):
        if self.scoreCam2 == 0:
            self.scoreCam2 = 1

            now = datetime.datetime.now()
            hour = now.hour
            minute = now.minute
            second = now.second

            nameVideoCam2 = self.toDay+'_'+str(hour)+'.'+str(minute)+'.'+str(second)+'_CAM2.avi'

            self.outCam2 = cv2.VideoWriter(nameVideoCam2, cv2.VideoWriter_fourcc(*'XVID'), self.fps, (640,480))
            messagebox.showinfo('Iniciando', 'Iniciando grabación de la CAM2')
            print("Record video CAM2 On")
        else:
            messagebox.showinfo('Aviso!','Grabación de la CAM2 en proceso...')

    def stopVideoCam1(self, args):
        if self.scoreCam1 == 1:
            self.scoreCam1 = 0
            self.segCAM1 = 0
            print("Stop video CAM1")
            self.outCam1.release()
            messagebox.showinfo('Grabación finalizada', 'El video ha sido guardado correctamente.')
        else:
            messagebox.showinfo('Aviso!','No se a iniciado la grabación en CAM1')

    def stopVideoCam2(self, agrs):
        if self.scoreCam2 == 1:
            self.scoreCam2 = 0
            self.segCAM2 = 0
            print("Stop video CAM2")
            self.outCam2.release()
            messagebox.showinfo('Grabación finalizada', 'El video ha sido guardado correctamente.')
        else:
            messagebox.showinfo('Aviso!', 'No se a iniciado la grabación en CAM2')
                
    def close_dropdown(self, dropdown):
        dropdown.dismiss()

    def set_FPS(self, fps, FPS_dropdown):
        self.fps = fps
        FPS_dropdown.select(fps)
        print(f"FPS: {fps}")

    def set_camera1(self, cam, button, cam_dropdown):
        self.cam1 = cam
        # button.text = f'-> Camera {cam + 1}'
        cam_dropdown.select(cam)
        self.start_captureCAM1()

    def set_camera2(self, cam, button, cam_dropdown):
        self.cam2 = cam
        cam_dropdown.select(cam)
        # button.text = f'-> Camera {cam + 1}'
        self.start_captureCAM2()

    def start_captureCAM1(self):
        self.capture1 = cv2.VideoCapture(self.cam1)
        Clock.schedule_interval(self.updateCAM1, 1.0 / self.fps)

    def start_captureCAM2(self):
        self.capture2 = cv2.VideoCapture(self.cam2)
        Clock.schedule_interval(self.updateCAM2, 1.0 / self.fps)

    def updateCAM1(self, dt):
        ret, frame = self.capture1.read()
        if ret: 
            
            h = 0
            m = 0
            s = 0
            # cv2.imwrite("imagen.jpg", frame) # Funciona!!!
            if self.scoreCam1 == 1:
                # frameToSave = cv2.flip(frame, 0)
                frameToSave = cv2.flip(frame, 1)

                rotate = frameToSave
                if self.rotatedCam1 == 0:
                    rotate = frameToSave
                elif self.rotatedCam1 == 1:
                    frameToSave = cv2.resize(frameToSave, (480, 640))
                    rotate = cv2.rotate(frameToSave, cv2.ROTATE_90_CLOCKWISE)
                elif self.rotatedCam1 == 2:
                    rotate = cv2.rotate(frameToSave, cv2.ROTATE_180)
                elif self.rotatedCam1 == 3:
                    frameToSave = cv2.resize(frameToSave, (480, 640))
                    rotate = cv2.rotate(frameToSave, cv2.ROTATE_90_COUNTERCLOCKWISE)

                self.outCam1.write(rotate)
                self.segCAM1 = self.segCAM1 + 1
                if (self.segCAM1 // self.fps) > 0:
                    total = self.segCAM1 // self.fps
                    horas, minutos, segundos = self.calcular_tiempo(total)
                    h = horas
                    m = minutos
                    s = segundos

            # convert it to texture
            frameAux = cv2.flip(frame, 0)
            frameAux = cv2.flip(frameAux, 1)

            if s < 10:
                s = f'0{s}'
            if m < 10:
                m = f'0{m}'
            if h < 10:
                h = f'0{h}'

            timeFrame = self.overlay(f'{h}:{m}:{s}')

            rotate = frameAux
            if self.rotatedCam1 == 0:
                rotate = frameAux
            elif self.rotatedCam1 == 1:
                frameAux = cv2.resize(frameAux, (480, 640))
                rotate = cv2.rotate(frameAux, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif self.rotatedCam1 == 2:
                rotate = cv2.rotate(frameAux, cv2.ROTATE_180)
            elif self.rotatedCam1 == 3:
                frameAux = cv2.resize(frameAux, (480, 640))
                rotate = cv2.rotate(frameAux, cv2.ROTATE_90_CLOCKWISE)
            
            rotate = cv2.addWeighted(rotate, 1,timeFrame,0.6,0)
            buf = rotate.tostring()
            
            # frame.shape[1] Ancho Columnas
            # frame.shape[0] Alto Filas
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        
            # display image from the texture
            self.web_cam1.texture = image_texture
        else:
            image = cv2.imread("img/notCamera.png")
            resized_image = cv2.resize(image, (100, 100))

            buf = cv2.flip(resized_image, 0).tostring()
            image_texture = Texture.create(
                size=(resized_image.shape[1], resized_image.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.web_cam1.texture = image_texture

    def updateCAM2(self, dt):
        ret2, frame2 = self.capture2.read()
        if ret2:
            
            h = 0
            m = 0
            s = 0
            # cv2.imwrite("imagen.jpg", frame) # Funciona!!!
            if self.scoreCam2 == 1:
                # frameToSave = cv2.flip(frame, 0)
                frameToSave = cv2.flip(frame2, 1)

                rotate = frameToSave
                if self.rotatedCam2 == 0:
                    rotate = frameToSave
                elif self.rotatedCam2 == 1:
                    frameToSave = cv2.resize(frameToSave, (480, 640))
                    rotate = cv2.rotate(frameToSave, cv2.ROTATE_90_CLOCKWISE)
                elif self.rotatedCam2 == 2:
                    rotate = cv2.rotate(frameToSave, cv2.ROTATE_180)
                elif self.rotatedCam2 == 3:
                    frameToSave = cv2.resize(frameToSave, (480, 640))
                    rotate = cv2.rotate(frameToSave, cv2.ROTATE_90_COUNTERCLOCKWISE)

                self.outCam2.write(rotate)
                self.segCAM2 = self.segCAM2 + 1
                if (self.segCAM2 // self.fps) > 0:
                    total = self.segCAM2 // self.fps
                    horas, minutos, segundos = self.calcular_tiempo(total)
                    h = horas
                    m = minutos
                    s = segundos

            # (480, 640, 3)

            # convert it to texture
            frameAux = cv2.flip(frame2, 0)
            frameAux = cv2.flip(frameAux, 1)
            
            if s < 10:
                s = f'0{s}'
            if m < 10:
                m = f'0{m}'
            if h < 10:
                h = f'0{h}'

            timeFrame = self.overlay(f'{h}:{m}:{s}')

            rotate = frameAux
            if self.rotatedCam2 == 0:
                rotate = frameAux
            elif self.rotatedCam2 == 1:
                frameAux = cv2.resize(frameAux, (480, 640))
                rotate = cv2.rotate(frameAux, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif self.rotatedCam2 == 2:
                rotate = cv2.rotate(frameAux, cv2.ROTATE_180)
            elif self.rotatedCam2 == 3:
                frameAux = cv2.resize(frameAux, (480, 640))
                rotate = cv2.rotate(frameAux, cv2.ROTATE_90_CLOCKWISE)

            rotate = cv2.addWeighted(rotate, 1,timeFrame,0.6,0)
            buf = rotate.tostring()

            image_texture = Texture.create(
                size=(frame2.shape[1], frame2.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.web_cam2.texture = image_texture
        else:
            image = cv2.imread("img/notCamera.png")
            resized_image = cv2.resize(image, (100, 100))

            buf = cv2.flip(resized_image, 0).tostring()
            image_texture = Texture.create(
                size=(resized_image.shape[1], resized_image.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.web_cam2.texture = image_texture

    def calcular_tiempo(self, segundos):
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos = segundos % 60
        return horas, minutos, segundos

    def rotate_imageCAM1(self, *args):
        # 0 normal
        # 1 90
        # 2 180
        # 3 270
        if self.rotatedCam1 == 3:
            self.rotatedCam1 = -1 
        
        self.rotatedCam1 = self.rotatedCam1 + 1
    
    def rotate_imageCAM2(self, *args):
        # 0 normal
        # 1 90
        # 2 180
        # 3 270
        if self.rotatedCam2 == 3:
            self.rotatedCam2 = -1 

        self.rotatedCam2 = self.rotatedCam2 + 1
      
    def overlay (self, text):
        # (480, 640)
        # Agregar lapso del tiempo en la imagen como layer
        width, height = (640, 480)
        image = np.zeros((height, width, 3), dtype=np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        text_color = (255, 255, 255)
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_x = int((width - text_size[0] - 10))
        text_y = int((height + text_size[1]) / 10)
        cv2.putText(image, 
                    text, 
                    (text_x, text_y), 
                    font, font_scale, 
                    text_color, 
                    font_thickness)
        

        textFps = "FPS: "+str(self.fps)
        text_size, _ = cv2.getTextSize(textFps, font, font_scale, font_thickness)
        text_x = int((width - text_size[0] + 10) / 20)
        text_y = int((height + text_size[1]) / 10)
        cv2.putText(image, 
                        textFps, 
                        (text_x, text_y), 
                        font, font_scale, 
                        text_color, 
                        font_thickness)
        
        image = cv2.flip(image, 0)
        #image = cv2.flip(image, 1)
        return image
    
if __name__ == '__main__':
    Tk().withdraw()
    CamApp().run()