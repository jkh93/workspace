import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.Image;
import java.awt.Point;
import java.awt.Toolkit;
import java.awt.event.WindowEvent;
import java.awt.image.MemoryImageSource;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintWriter;

import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JPanel;

public class MyFrame {

	// laptop resolution
	int screenx = 1366;
	int screeny = 768;
	
	int j = 0;
	
	int[] coordinates = {
			234,345, // junk coordinate
			456,567, // junk coordinate
			0,0,
			500,500,
			500,10,
			10,650,
			1100,400,
			0,0, // repeat for hidden cursor
			500,500,
			500,10,
			10,650,
			1100,400};
	Procedure normal = new Procedure(coordinates);
	Procedure one = new Procedure(coordinates);
	Procedure two = new Procedure(coordinates);
	
	final int CLEN = 12;
	final int CTHR = 6;
	
	JFrame frame = null;
	JPanel back_panel = null;
	MyJPanel panel = null;
	
	PrintWriter writer = null;
	
	Cursor cursor = new Cursor(Cursor.DEFAULT_CURSOR);
	int[] pixels = new int[16 * 16];
	Image image = Toolkit.getDefaultToolkit().createImage(
	        new MemoryImageSource(16, 16, pixels, 0, 16));
	Cursor transparentCursor =
	        Toolkit.getDefaultToolkit().createCustomCursor
	             (image, new Point(0, 0), "invisibleCursor");
	
	int i = 0;
	
	boolean task = false;
	
	String name = null;
	int group = 0;
	String method = null;
	
	boolean expend = false;

	long start_time = 0;
	long end_time = 0;
	long dialog_duration = 0;
	
	Point loc = new Point(0, 0);
	
	public MyFrame(String n, int g) throws IOException {
		name = n;
		writer = new PrintWriter(new FileOutputStream(new File(name+".txt"), true));
		group = g;
		setMethod();
		init();
		setST();
		task();
	}
	
	private void init() {
		frame = new JFrame("Experiment");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		back_panel = new JPanel();
		back_panel.setPreferredSize(new Dimension(1366, 768));
		panel = new MyJPanel(loc, this);
		back_panel.add(panel);
		frame.getContentPane().add(back_panel);
		frame.pack();
		frame.setVisible(true);
		frame.setEnabled(true);
	}
	
	private void setMethod() {
		switch(group) {
			case 1:
				method = "normal";
				break;
			case 2:
				method = "normal";
				break;
			case 3:
				method = "one";
				break;
			case 4:
				method = "one";
				break;
			case 5:
				method = "two";
				break;
			case 6:
				method = "two";
				break;
			default:
				System.out.println("shouldn't be here");
		}
	}
	
	public void task() {
		// start up dialog
		long dialog_start = System.nanoTime();
		JOptionPane.showMessageDialog(frame, "The cursor movement method is "
				+ getMethod().toUpperCase()
				+ "\n\n"
				+ "Please move the cursor inside the target box as fast as possible");
		long dialog_end = System.nanoTime();
		dialog_duration = (dialog_end-dialog_start);
		loc = getNext();
		// write
		panel.updateLocation(loc);
		// check expend
		if (expend) {
			writer.close();
			frame.dispatchEvent(new WindowEvent(frame, WindowEvent.WINDOW_CLOSING));
		}
		repaint();
	}
	
	public void setET() {
		end_time = System.nanoTime();
	}
	
	public void setST() {
		start_time = System.nanoTime();
	}
	
	public void write(long time) {
		String cur = "hidden";
		if (frame.getCursor().getType() == Cursor.DEFAULT_CURSOR) cur = "visible";
		writer.write(name+" "+method+" "+cur+" "+(time-dialog_duration)/1000000+"\n");
	}
	
	private void repaint() {
		panel.repaint();
	}
	
	private String getMethod() {
		String r = "normal";
		if (group==1) {
			if (j<12) {
				r="normal";
			} else if (j<24) {
				r="one";
			} else {
				r="two";
			}
		} else if (group==2) {
			if (j<12) {
				r="normal";
			} else if (j<24) {
				r="two";
			} else {
				r="one";
			}
		} else if (group==3) {
			if (j<12) {
				r="one";
			} else if (j<24) {
				r="normal";
			} else {
				r="two";
			}
		} else if (group==4) {
			if (j<12) {
				r="one";
			} else if (j<24) {
				r="two";
			} else {
				r="normal";
			}
		} else if (group==5) {
			if (j<12) {
				r="two";
			} else if (j<24) {
				r="normal";
			} else {
				r="one";
			}
		} else if (group==6) {
			if (j<12) {
				r="two";
			} else if (j<24) {
				r="one";
			} else {
				r="normal";
			}
		}
		return r;
	}
	
	private Point getNext() {
		j++;
		if (group == 1) {
			if (method.equals("normal")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return normal.getPoint(i-1);
				}
				else {
					System.out.println("in here");
					frame.setCursor(cursor);
					i=1;
					method = "one";
					return one.getPoint(i-1);
				}
			} else if (method.equals("one")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return one.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "two";
					return two.getPoint(i-1);
				}
			} else if (method.equals("two")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return two.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					expend = true;
				}
			}
		} else if (group == 2) {
			if (method.equals("normal")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return normal.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "two";
					return two.getPoint(i-1);
				}
			} else if (method.equals("two")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return two.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "one";
					return one.getPoint(i-1);
				}
			} else if (method.equals("one")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return one.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					expend = true;
				}
			}
		} else if (group == 3) {
			if (method.equals("one")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return one.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "normal";
					return normal.getPoint(i-1);
				}
			} else if (method.equals("normal")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return normal.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "two";
					return two.getPoint(i-1);
				}
			} else if (method.equals("two")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return two.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					expend = true;
				}
			}
		} else if (group == 4) {
			if (method.equals("one")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return one.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "two";
					return two.getPoint(i-1);
				}
			} else if (method.equals("two")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return two.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "normal";
					return normal.getPoint(i-1);
				}
			} else if (method.equals("normal")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return normal.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					expend = true;
				}
			}
		} else if (group == 5) {
			if (method.equals("two")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return two.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "normal";
					return normal.getPoint(i-1);
				}
			} else if (method.equals("normal")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return normal.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "one";
					return one.getPoint(i-1);
				}
			} else if (method.equals("one")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return one.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					expend = true;
				}
			}
		} else if (group == 6) {
			if (method.equals("two")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return two.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "one";
					return one.getPoint(i-1);
				}
			} else if (method.equals("one")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return one.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					i=1;
					method = "normal";
					return normal.getPoint(i-1);
				}
			} else if (method.equals("normal")) {
				if (i<CLEN) {
					if (i>CTHR) frame.setCursor(transparentCursor);
					i++;
					return normal.getPoint(i-1);
				}
				else {
					frame.setCursor(cursor);
					expend = true;
				}
			}
		}
		System.out.println("finished experiment");
		return loc; // shouldn't hit this
	}
	
}
