# Importamos herramientas de trabajo
from tkinter import ANCHOR, BOTH, CENTER, E, END, W, Button, Entry, Frame, Label, Tk, ttk
import sqlite3
import time
import random
import math

# Como todo programa de escritorio creamos clases para trabajar con POO
class Parking:
    
    baseDeDatos = 'base.db'
    valorHora = 1200
    promoParqueoGratis = 120

    # Iniciamos nuestra clase con el metodo init
    def __init__(self, ventana: Tk, nombreDeLaCompania: str) -> None:
        
        # Personalizamos nuestra ventana
        self.ventana = ventana
        self.ventana.title(f'Sistema de parqueo {nombreDeLaCompania}')
        self.ventana.resizable(False, False)
        self.ventana.iconbitmap('parqueo.ico')
        
        # Creamos un container
        self.frame = ttk.LabelFrame(self.ventana)
        self.frame.grid(row = 0, column = 0, padx = 100, pady = 25)
        
        # Comenzamos a ingresar el orden de FILAS
        
        # -- FILA 1
        Label(self.frame, text = 'ENTRADA').grid(row = 1, column = 0, columnspan = 2)

        # -- FILA 2
        Label(self.frame, text = '¿Se le dio tarjeta? (SI o NO):').grid(row = 2, column = 0)
        self.tarjeta = Entry(self.frame)
        self.tarjeta.focus()
        self.tarjeta.grid(row = 2, column = 1)

        # -- FILA 3
        Label(self.frame, text = 'Placa (AAA-000):').grid(row = 3, column = 0)
        self.placaEntra = Entry(self.frame)
        self.placaEntra.grid(row = 3, column = 1)

        # -- FILA 4
        self.boton1 = Button(self.frame, text='Entrar', width = 10, command = self.EntraVehiculo).grid(row = 4, columnspan = 2)
        
        # -- FILA 5
        self.message = Label(self.frame, text = '', fg = 'red')
        self.message.grid(row = 5, column = 0, columnspan = 2)

        # -- FILA 6
        self.consulta = Entry(self.frame)
        self.consulta.grid(row = 6, column = 0)
        self.boton2 = Button(self.frame, text = 'Consultar placa', command = self.ConsultarPlaca).grid(row = 6, column = 1)

        # -- FILA 7
        self.auxmessage = Label(self.frame, text = '')
        self.auxmessage.grid(row = 7, column = 0, columnspan = 2)

    # Hacemos una función para acceder a la base de datos y reusar codigo
    def IniciarConsultaSQL(self, consulta: str, parametros = ()) -> list:
        with sqlite3.connect(self.baseDeDatos) as database:
            cursor = database.cursor()
            result = cursor.execute(consulta, parametros)
            database.commit()
        return result

    # Identificamos cuando entra un vehiculo e identificamos si tiene tarjeta o no
    def EntraVehiculo(self) -> None:
        tarjeta = self.tarjeta.get().replace(' ', '').upper()
        horaEntrada = str(time.time())
        numeroTarjeta = int(random.random()*1000)
        placa = self.placaEntra.get().replace(' ', '').replace('-', '').upper()
        if tarjeta == 'SI' and len(placa) == 6:
            consulta = f'INSERT INTO VehiculosConTarjeta(placa, tarjeta, horaEntrada) VALUES (?, ?, ?)'
            parametros = (placa, numeroTarjeta, horaEntrada)
            self.IniciarConsultaSQL(consulta, parametros)
            self.message['text'] =  'Vehiculo agregado correctamente'
        elif tarjeta == 'NO' and len(placa) == 6:
            consulta = f'INSERT INTO VehiculosSinTarjeta(placa, horaEntrada) VALUES (?, ?)'
            parametros = (placa, horaEntrada)
            self.IniciarConsultaSQL(consulta, parametros)
            self.message['text'] =  'Vehiculo agregado correctamente'
        else:
            self.message['text'] = 'ERROR, Ingrese datos validos!'
            self.tarjeta.delete(0, END)
            self.placaEntra.delete(0, END)
        self.tarjeta.delete(0, END)
        self.placaEntra.delete(0, END)

    # Lee la placa que se consulta y retorna muchos datos en pantalla
    def ConsultarPlaca(self) -> None:
        self.placaConsulta = self.consulta.get().replace(' ', '').replace('-', '').upper()
        self.message.destroy()
        placa = self.placaConsulta
        tieneTarjeta = ''
        if self.buscarVehiculo(placa)[0]:
            tieneTarjeta = 'SI'
        else:
            tieneTarjeta = 'NO'

        self.tiempoTranscurrido = self.calcularTiempo(self.buscarVehiculo(placa)[1])
        valorAPagarHastaElMomento = self.valorHora * self.tiempoTranscurrido

        self.message1 = Label(self.frame, text=f'Vehiculo = {placa}')
        self.message1.grid(row = 8, columnspan = 2)
        
        self.message2 = Label(self.frame, text=f'Tarjeta de parqueadero = {tieneTarjeta}')
        self.message2.grid(row = 9, columnspan = 2)
        
        if self.tiempoTranscurrido == 1:
            self.message3 = Label(self.frame, text=f'Tiempo transcurrido = {self.tiempoTranscurrido} hora')
        else:
            self.message3 = Label(self.frame, text=f'Tiempo transcurrido = {self.tiempoTranscurrido} horas')
        self.message3.grid(row = 10, columnspan = 2)

        self.message4 = Label(self.frame, text=f'Valor a pagar = ${valorAPagarHastaElMomento} pesos')
        self.message4.grid(row = 11, columnspan = 2)

        self.botonAux1 = Button(self.frame, text = 'Fin Consulta', command = self.finDeConsulta)
        self.botonAux1.grid(row = 12, column = 0, sticky = W + E)

        self.botonAux2 = Button(self.frame, text = 'Pagar', command = self.pagar)
        self.botonAux2.grid(row = 12, column = 1, sticky = W + E)

        self.consulta.delete(0, END)

    # Busca el vehiculo por su placa y devuelve datos en lista  
    def buscarVehiculo(self, placa: str) -> list:
        consulta = 'SELECT * FROM VehiculosConTarjeta'
        datos = self.IniciarConsultaSQL(consulta)
        lista = []
        for dato in datos:
            if dato[1] == placa:
                lista.append(True)
                lista.append(dato[3])
                lista.append(dato[0])
                self.auxmessage['fg'] = 'green'
                self.auxmessage['text'] = '¡Vehiculo Encontrado!'
                
            else:
                consulta = 'SELECT * FROM VehiculosSinTarjeta'
                datos = self.IniciarConsultaSQL(consulta)
                for dato in datos:
                    if dato[1] == placa:
                        lista.append(False)
                        lista.append(dato[2])
                        lista.append(dato[0])
                        self.auxmessage['fg'] = 'green'
                        self.auxmessage['text'] = '¡Vehiculo Encontrado!'
                    else:
                        self.auxmessage['fg'] = 'red'
                        self.auxmessage['text'] = '¡Vehiculo no Encontrado!'

        
        return lista

    # Calcula el tiempo segun la hora de ingreso
    def calcularTiempo(self, horaIngreso: str) -> int:
        tiempoActual = time.time()
        if math.ceil((tiempoActual - float(horaIngreso))/60) <= 15:
            tiempoTranscurrido = 0
        else:
            tiempoTranscurrido = math.ceil((tiempoActual - float(horaIngreso))/3600)
        return tiempoTranscurrido

    # Borra el menu que despliega la funcion 'consultar placa'
    def finDeConsulta(self) -> None:
        self.message1.destroy()
        self.message2.destroy()
        self.message3.destroy()
        self.message4.destroy()
        self.botonAux1.destroy()
        self.botonAux2.destroy()

    # Revisa si el cliente es digno de la promo de parqueo gratis o si no llama a la funcion cobrar
    def pagar(self) -> None:
        if self.tiempoTranscurrido == 0:
            self.salir()
        else:
            placa = self.placaConsulta
            consulta = 'SELECT * FROM HistorialDeVehiculos'
            datos = self.IniciarConsultaSQL(consulta)
            for dato in datos:
                if dato[1] == placa:
                    if dato[2] >= float(self.promoParqueoGratis):
                        print('Gracias por ser un cliente fiel. En agradecimiento tiene el parqueadero gratis')
                    else:
                        self.cobrar()
                else:
                    self.cobrar()

    # Realiza la operacion de pago y entrega de devueltas si las hay
    def cobrar(self) -> None:
        self.finDeConsulta()
        self.auxmessage['fg'] = 'black'
        self.auxmessage['text'] = 'Ingresa el dinero en el cajero'
        self.ClientePaga = Entry(self.frame)
        self.ClientePaga.grid(row = 8, column = 0)
        self.botonAux1 = Button(self.frame, text = 'Realizar Pago', command = self.Comparar)
        self.botonAux1.grid(row = 8, column = 1)
    
    # Compara el precio total del parqueadero con el valor pagado
    def Comparar(self) -> None:
        self.ValorPagado = int(self.ClientePaga.get())
        valorACobrar = self.valorHora * self.tiempoTranscurrido
        diferencia = int(self.ValorPagado) - valorACobrar
        if diferencia == 0:
            self.ClientePaga.delete(0, END)
            self.ClientePaga.destroy()
            self.salir()
        elif diferencia > 0:
            print(f'Toma tus devueltas {diferencia}')
            self.ClientePaga.delete(0, END)
            self.ClientePaga.destroy()
            self.salir()
        else:
            print(f'¡UY!, Te falta dinero {diferencia}')

    # Agrega el vehiculo a el historial de vehiculos y dar 15 minutos de salida
    def salir(self) -> None:
        placa = self.placaConsulta
        tarjeta = self.buscarVehiculo(placa)[0]
        idVehiculo = self.buscarVehiculo(placa)[2]
        self.finDeConsulta()
        if tarjeta:
            consulta = f'DELETE FROM VehiculosConTarjeta WHERE id={idVehiculo}'
            self.IniciarConsultaSQL(consulta)
        else:
            consulta = f'DELETE FROM VehiculosSinTarjeta WHERE id={idVehiculo}'
            self.IniciarConsultaSQL(consulta)
        if self.tiempoTranscurrido != 0:
            print('Listo, tienes 15 minutos para salir, gracias por tu visita')
            consulta = 'INSERT INTO HistorialDeVehiculos(placa, tiempoAcumulado) VALUES (?, ?)'
            parametros = (placa, str(self.tiempoTranscurrido))
            self.IniciarConsultaSQL(consulta, parametros)
        else:
            print('Listo, tienes 15 minutos para salir, gracias por tu visita')
    

if __name__ == '__main__':
    ventana = Tk()
    aplication = Parking(ventana, 'Centro Comercial La Estación')
    ventana.mainloop()