import wx

#https://c64.ch/programming/VICMCRC


class VIC(wx.Frame):
    """
    Calculator for VIC-Values of the C64
    """

    __DEFAULT_DD00 = '10010111'
    __DEFAULT_D018 = '00010101'
    __MASK_DD00 = '00000011'
    __MASK_D018 = '11111110'

    def __init__(self, parent=None, style=0, *args, **kwargs):
        super(VIC, self).__init__(parent, style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|style, *args, **kwargs)
        self.__initUI()
        self.Title = 'C64 VIC Calculator'
        self.SetSize(wx.Size(300,220))
        self.Show(True)

    def __initUI(self):
        """
        Fenster aufbauen
        :return:
        """
        topPanel = wx.Panel(self)
        sizer = wx.GridBagSizer(3, 3)
        row = 0

        #Bank
        control = wx.StaticText(topPanel, -1, label='Bank:', name='lblBank')
        sizer.Add(control, pos=(row, 0))
        self.__bank = wx.ComboBox(topPanel, choices=['$0000-$3FFF', '$4000-$7FFF', '$8000-$BFFF', '$C000-$FFFF'],
                                  name='comboBank', style=wx.CB_READONLY|wx.CB_DROPDOWN)
        self.__bank.Bind(wx.EVT_COMBOBOX, self.__BankSelected)
        self.__bank.SetToolTip('Bank wählen')
        sizer.Add(self.__bank, pos=(row, 1), flag=wx.EXPAND, border=5)
        row += 1

        #Char Address
        control = wx.StaticText(topPanel, -1, label='Charset Address:', name='lblCharset')
        sizer.Add(control, pos=(row, 0))
        self.__charset = wx.ComboBox(topPanel, choices=[], name='comboCharset', style=wx.CB_READONLY|wx.CB_DROPDOWN)
        self.__charset.Disable()
        self.__charset.Bind(wx.EVT_COMBOBOX, self.__comboSelected)
        self.__charset.SetToolTip('Addresse, wo der Zeichensatz gesucht wird')
        sizer.Add(self.__charset, pos=(row, 1), flag=wx.EXPAND, border=5)
        row += 1

        #Screen Address
        control = wx.StaticText(topPanel, -1, label='Screen Address:', name='lblScreen')
        sizer.Add(control, pos=(row, 0))
        self.__screen = wx.ComboBox(topPanel, choices=[], name='comboScreen', style=wx.CB_READONLY|wx.CB_DROPDOWN)
        self.__screen.Disable()
        self.__screen.Bind(wx.EVT_COMBOBOX, self.__comboSelected)
        self.__screen.SetToolTip('Addresse, wo der Bildschirmspeicher liegt')
        sizer.Add(self.__screen, pos=(row, 1), flag=wx.EXPAND, border=5)
        row += 1

        row += 1
        #DD00
        control = wx.StaticText(topPanel, -1, label='DD00:', name='lblDD00')
        sizer.Add(control, pos=(row, 0))
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.__bin_dd00 = wx.TextCtrl(topPanel, name='binDD00')
        self.__bin_dd00.Disable()
        self.__bin_dd00.SetMaxLength(8)
        self.__bin_dd00.Bind(wx.EVT_TEXT, self.__CheckText)
        self.__bin_dd00.SetToolTip('Bitmuster, welches in DD00 steht\n'
                                   'Bits, welche für andere Funktionen sind, werden mit X dargestellt')
        box.Add(self.__bin_dd00)
        self.__hex_dd00 = wx.TextCtrl(topPanel, name='hexDD00', size=wx.Size(30,-1))
        self.__hex_dd00.Disable()
        self.__hex_dd00.SetMaxLength(2)
        self.__hex_dd00.Bind(wx.EVT_TEXT, self.__CheckText)
        self.__hex_dd00.SetToolTip('Hexadezimale Schreibweise, welche in DD00 steht.\n'
                                   'X-Bits werden mit dem Standardwert versehen')
        box.Add(self.__hex_dd00)
        sizer.Add(box, pos=(row, 1))
        row += 1


        #D018
        control = wx.StaticText(topPanel, -1, label='D018:', name='lblD018')
        sizer.Add(control, pos=(row, 0))
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.__bin_d018 = wx.TextCtrl(topPanel, name='binD018')
        self.__bin_d018.Disable()
        self.__bin_d018.SetMaxLength(8)
        self.__bin_d018.Bind(wx.EVT_TEXT, self.__CheckText)
        self.__bin_d018.SetToolTip('Bitmuster, welches in D018 steht.\n'
                                   'Bits, welche für andere Funktionen sind, werden mit X dargestellt')
        box.Add(self.__bin_d018)
        self.__hex_d018 = wx.TextCtrl(topPanel, name='hexD018', size=wx.Size(30,-1))
        self.__hex_d018.Disable()
        self.__hex_d018.SetMaxLength(2)
        self.__hex_d018.Bind(wx.EVT_TEXT, self.__CheckText)
        self.__hex_d018.SetToolTip('Hexadezimale Schreibweise, welche in D018 steht.\n'
                                   'X-Bits werden mit dem Standardwert versehen')
        box.Add(self.__hex_d018)

        sizer.Add(box, pos=(row, 1))
        row += 1

        control = wx.StaticText(topPanel, -1, label='Written 2026 by 64erGrufti')
        control.Font = wx.Font(7, wx.DECORATIVE, wx.DEFAULT, wx.NORMAL)
        sizer.Add(control, pos=(row, 0))

        wrapper = wx.BoxSizer(wx.VERTICAL)
        wrapper.Add(sizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        topPanel.SetSizer(wrapper)
        self.Bind(wx.EVT_CLOSE, self.__onExit)

    def __onExit(self, event):
        """
        What to do on closing the window
        :param event:
        :return:
        """
        self.Destroy()

    def __CheckText(self, event):
        """
        Eingabe in den Textboxen auf formelle Gültigkeit prüfen
        :param event:
        :return:
        """
        obj = event.GetEventObject()
        value = obj.GetValue()
        pos = obj.GetInsertionPoint()
        if obj.Name.startswith('hex'):  # Es war eine Hex-Box
            if not all(v in '0123456789abcdefABCDEF' for v in value):
                newValue = ''
                for v in value:
                    if not v in '0123456789abcdefABCDEF': v = '0'
                    newValue += v
                obj.ChangeValue(newValue)
                obj.SetInsertionPoint(pos)
            self.hex2bin()
            self.bin2Combo()
        else:  # Es war eine Binärbox
            # Ungültige Zeichen ersetzen
            if not all(v in '01xX' for v in value):
                newValue = ''
                for v in value:
                    if not v in '01xX':
                        v='0'
                    newValue += v
                obj.ChangeValue(newValue)
                obj.SetInsertionPoint(pos)
            self.bin2hex()
            self.bin2Combo()

    def __BankSelected(self, event):
        """
        Eventfunktion der Bankauswahl
        :param event:
        :return:
        """
        self.bank2Combo()
        self.bank2bits()

    def __comboSelected(self, event):
        """
        Eventfunktion der Comboboxen Bildschirm- und Charspeicher
        :param event:
        :return:
        """
        self.bank2bits()

    def bank2Combo(self):
        """
        Füllt die Comboboxen Screen- und Charspeicher aus der Bankauswahl
        :return:
        """
        self.__charset.Enable()
        self.__screen.Enable()
        self.__bin_d018.Enable()
        self.__hex_d018.Enable()
        self.__bin_dd00.Enable()
        self.__hex_dd00.Enable()

        charset = self.__charset.GetSelection()
        if charset == -1: charset = 0
        self.__charset.Clear()

        screen = self.__screen.GetSelection()
        if screen == -1:
            screen = 0

        #charset
        match self.__bank.GetSelection():
            case 0: # $0000-3FFF
                self.__charset.AppendItems(['$0000-$07FF','$0800-$0FFF',
                                           '$D000-$D7FF','$D800-$DFFF',#'$1000-$17FF','$1800-$1FFF',
                                           '$2000-$27FF','$2800-$2FFF',
                                           '$3000-$37FF','$3800-$3FFF'])
            case 1: # $4000-$7FFF
                self.__charset.AppendItems(['$4000-$47FF','$4800-$4FFF',
                                           '$5000-$57FF','$5800-$5FFF',
                                           '$6000-$67FF','$6800-$6FFF',
                                           '$7000-$77FF','$7800-$7FFF'])
            case 2: # $8000-$BFFF
                self.__charset.AppendItems(['$8000-$87FF','$8800-$8FFF',
                                           '$D000-$D7FF','$D800-$DFFF',#'$9000-$97FF','$9800-$9FFF',
                                           '$A000-$A7FF','$A800-$AFFF',
                                           '$B000-$B7FF','$B800-$BFFF'])
            case 3: # $C000-$FFFF
                self.__charset.AppendItems(['$C000-$C7FF','$C800-$CFFF',
                                           '$D000-$D7FF','$D800-$DFFF',
                                           '$E000-$E7FF','$E800-$EFFF',
                                           '$F000-$F7FF','$F800-$FFFF'])

        # Screen
        self.__screen.Clear()
        match self.__bank.GetSelection():
            case 0: # $0000-3FFF
                self.__screen.AppendItems(['$0000-$03FF','$0400-$07FF',
                                           '$0800-$0BFF','$0C00-$0FFF',
                                           '$1000-$13FF','$1400-$17FF',
                                           '$1800-$1BFF','$1C00-$1FFF',
                                           '$2000-$23FF','$2400-$27FF',
                                           '$2800-$2BFF','$2C00-$2FFF',
                                           '$3000-$33FF','$3800-$37FF',
                                           '$3800-$3BFF','$3C00-$3FFF'])
            case 1: # $4000-$7FFF
                self.__screen.AppendItems(['$4000-$43FF','$4400-$47FF',
                                           '$4800-$4BFF','$4C00-$4FFF',
                                           '$5000-$53FF','$5400-$57FF',
                                           '$5800-$5BFF','$5C00-$5FFF',
                                           '$6000-$63FF','$6400-$67FF',
                                           '$6800-$6BFF','$6C00-$6FFF',
                                           '$7000-$73FF','$7800-$77FF',
                                           '$7800-$7BFF','$7C00-$7FFF'])
            case 2: # $8000-$BFFF
                self.__screen.AppendItems(['$8000-$83FF','$8400-$87FF',
                                           '$8800-$8BFF','$8C00-$8FFF',
                                           '$9000-$93FF','$9400-$97FF',
                                           '$9800-$9BFF','$9C00-$9FFF',
                                           '$A000-$A3FF','$A400-$A7FF',
                                           '$A800-$ABFF','$AC00-$AFFF',
                                           '$B000-$B3FF','$B800-$B7FF',
                                           '$B800-$BBFF','$BC00-$3BFF'])
            case 3: # $C000-$FFFF
                self.__screen.AppendItems(['$C000-$C3FF','$C400-$C7FF',
                                           '$C800-$CBFF','$CC00-$CFFF',
                                           '$D000-$D3FF','$D400-$D7FF',
                                           '$D800-$DBFF','$DC00-$DFFF',
                                           '$E000-$E3FF','$E400-$E7FF',
                                           '$E800-$EBFF','$EC00-$EFFF',
                                           '$F000-$F3FF','$F800-$F7FF',
                                           '$E800-$FBFF','$FC00-$FFFF'])

        self.__charset.SetSelection(charset)
        self.__screen.SetSelection(screen)

    def bank2bits(self):
        """
        Berechnet die Binärwerte von DD00 und D018 aus den Comboboxen
        :param event:
        :return:
        """
        bits = (~self.__bank.GetSelection()) & 3
        self.__bin_dd00.ChangeValue(self.convertBits(f'{bits:08b}', self.__MASK_DD00, self.__DEFAULT_DD00))

        #Bildschirmspeicher
        screen = self.__screen.GetSelection() << 4

        #Zeichenspeicher
        char = self.__charset.GetSelection() << 1

        d018 = screen | char
        self.__bin_d018.ChangeValue(self.convertBits(f'{d018:08b}',self.__MASK_D018, self.__DEFAULT_D018))

        #In Hex umwandeln
        self.bin2hex()

    def bin2hex(self):
        """
        Wandelt die Binärwerte von DD00 und D018 in Hex um
        :return:
        """
        dd00 = self.__bin_dd00.GetValue()
        if len(dd00) > 0:
            dd00 = int(self.filterBits(dd00, self.__DEFAULT_DD00),2)
            self.__hex_dd00.ChangeValue(f'{dd00:02X}')

        d018 = self.__bin_d018.GetValue()
        if len(d018) > 0:
            d018 = int(self.filterBits(d018, self.__DEFAULT_D018),2)
            self.__hex_d018.ChangeValue(f'{d018:02X}')

    def hex2bin(self):
        """
        Wandelt die Hexwerte von DD00 und D018 in Binär um
        :return:
        """
        dd00 = self.__hex_dd00.GetValue()
        if len(dd00) > 0:
            dd00 = int(dd00.lower(),16)
            self.__bin_dd00.ChangeValue(self.convertBits(f'{dd00:08b}', self.__MASK_DD00, self.__DEFAULT_DD00))

        d018 = self.__hex_d018.GetValue()
        if len(d018) > 0:
            d018 = int(d018.lower(),16)
            self.__bin_d018.ChangeValue(self.convertBits(f'{d018:08b}', self.__MASK_D018, self.__DEFAULT_D018))

    def bin2Combo(self):
        """
        Berechnet die Combobox-Werte aus den Binärwerten von DD00 und D018
        :return:
        """
        dd00 = self.__bin_dd00.GetValue()
        if len(dd00) > 0:
            dd00 = int(dd00.lower().replace('x', '0'),2)
            bank = ~dd00 & 3
            self.__bank.SetSelection(bank)
            self.bank2Combo()

        d018 = self.__bin_d018.GetValue()
        if len(d018) > 0:
            d018 = int(d018.lower().replace('x', '0'),2)
            screen = (d018 & 240) >> 4
            self.__screen.SetSelection(screen)
            charset = (d018 & 14) >> 1
            self.__charset.SetSelection(charset)

    def convertBits(self, pattern: str, mask: str, default:str) -> str:
        """
        Bitwise:
        If mask=0 -> X
        If mask=1: If pattern is not X -> pattern
                    If pattern is X -> default
        :param pattern: Bits pattern (0,1,X)
        :param mask: Bitmask (0,1)
        :param default: Default values (0,1)
        :return:
        """
        ret = ''
        for p, m, d in zip(pattern, mask, default):
            if m == '1':
                if p.lower() != 'x':
                    ret += p
                else:
                    ret += d
            else:
                ret += 'X'
        return ret

    def filterBits(self, bits: str, default:str) -> str:
        """
        Bitwise: X-Values to defaults
        :param bits: Bits to be filtered
        :param default: Default values
        :return: Filtered bits
        """
        return ''.join([b if b.lower() != 'x' else d for b, d in zip(bits, default)])

if __name__ == '__main__':
    app = wx.App()
    VIC()
    app.MainLoop()