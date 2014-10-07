import java.awt.BorderLayout;
import java.awt.Dimension;
import javax.swing.JFrame;
import javax.swing.JPanel;

public class Junk {	
	
	// phone resolution in landscape
	int phonex = 1280;
	int phoney = 768;
	
	// laptop resolution
	int screenx = 1366;
	int screeny = 768;
	
	// tv resolution
	int tvx = 1920;
	int tvy = 1080;
	
	public static void main(String args[]) {
		for (int i = 0; i < args.length; i++) {
			System.out.println(args[i]);
		}
		JFrame frame = new JFrame("HI");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		
		JPanel back_panel = new JPanel();
		back_panel.setPreferredSize(new Dimension(1366, 768));
		
		frame.getContentPane().add(back_panel, BorderLayout.CENTER);
		frame.pack();
		
		MyJPanel panel = new MyJPanel(25, 25);
		back_panel.add(panel);
		panel.setMaxDimension(1366, 768);
		
		
//		JLabel label = new JLabel();
//		label.setPreferredSize(new Dimension(300, 100));
//		frame.getContentPane().add(panel, BorderLayout.CENTER);
//		frame.pack();
		frame.setVisible(true);
		frame.setEnabled(true);
	}
}
