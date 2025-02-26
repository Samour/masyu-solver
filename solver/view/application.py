import tkinter as tk


class Application(tk.Frame):

  def __init__(self, master):
    super().__init__(master)
    self._is_closing = False
    self._message = None
    self._close_button = None

  def render(self):
    if self._message is not None:
      self._message.destroy()
    if self._close_button is not None:
      self._close_button.destroy()

    if not self._is_closing:
      self._render_main()
    else:
      self._render_closing()
    self.pack(padx=50, pady=30)
  
  def _render_main(self):
    self._message = tk.Label(self, text="Hello TKinter!")
    self._message.pack()
    self._close_button = tk.Button(self, text="Hello", command=self._command_close)
    self._close_button.pack(pady=10)

  def _render_closing(self):
    self._message = tk.Label(self, text="Goodbye TKinter!")
    self._message.pack()

  def _command_close(self):
    self._is_closing = True
    self.render()
    self.after(1_000, self.master.destroy)


def main():
  root = tk.Tk()
  app = Application(root)
  app.master.title('Masyu Solver')
  app.master.geometry('+500+200')
  app.render()
  root.mainloop()
