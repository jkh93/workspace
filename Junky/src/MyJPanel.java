import java.awt.Color;
import java.awt.Dimension;
import java.awt.Point;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;


public  class MyJPanel extends JPanel {
	
	MyFrame frame = null;
	
	public MyJPanel(Point loc, MyFrame parent) {
		frame = parent;
		setPreferredSize(new Dimension(100, 100));
		setBackground(Color.GREEN);
		setLocation(loc.x, loc.y);
		addMouseListener(new MouseAdapter() {
			@Override
			public void mouseEntered(MouseEvent e) {
		        java.awt.Point p = new java.awt.Point(e.getLocationOnScreen());
		        SwingUtilities.convertPointFromScreen(p, e.getComponent());
		        if(e.getComponent().contains(p)) {
		        	// moving handled in myframe
		        	// should return true for task complete
		        	frame.task();
		        	frame.setET();
		        	long d = (frame.end_time - frame.start_time);
		        	frame.write(d);
		        	frame.setST();
		        }
			}
		});
	}
	
	public void updateLocation(Point loc) {
		this.setLocation(loc);
	}
}
