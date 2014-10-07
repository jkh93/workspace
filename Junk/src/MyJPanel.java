import java.awt.Color;
import java.awt.Dimension;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.Random;

import javax.swing.JPanel;
import javax.swing.SwingUtilities;


public  class MyJPanel extends JPanel {
	
	Random rand = new Random();
	int max_x = 0;
	int max_y = 0;
	
	int box_x;
	int box_y;
	
	public MyJPanel(int x, int y) {
		box_x = x;
		box_y = y;
		setPreferredSize(new Dimension(box_x, box_y));
		setBackground(Color.BLUE);
		setLocation(50, 50);
		addMouseListener(new MouseAdapter() {
			@Override
			public void mouseEntered(MouseEvent e) {
		        java.awt.Point p = new java.awt.Point(e.getLocationOnScreen());
		        SwingUtilities.convertPointFromScreen(p, e.getComponent());
		        if(e.getComponent().contains(p)) {
		        	int m = rand.nextInt(max_x-box_x-32); // 32 for launcher
		        	int n = rand.nextInt(max_y-box_y-24); // 24 for top bar
		        	setLocation(m, n);
		        }
			}
		});
	}
	
	public void setMaxDimension(int x, int y) {
		this.max_x = x;
		this.max_y = y;
    	System.out.println(max_x+" "+max_y);
	}
}
