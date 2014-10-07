import java.awt.Cursor;
import java.awt.MouseInfo;
import java.awt.Point;
import java.awt.Robot;
import java.io.IOException;

import org.apache.commons.io.input.TailerListenerAdapter;



public class MyTailerListener extends TailerListenerAdapter {
	
	MyFrame myframe = null;
	
	String[] split = null; // holder
	String state = "UP"; // finger states {DOWN, MOVE, UP}
	Point sp = null; // screen position
	Point np = new Point(0, 0); // new phone position
	Point op = new Point(0, 0); // old phone position
	Robot robot = null; // robot to move mouse
	
	// construct with robot to move mouse
	public MyTailerListener(Robot robot, String args[]) throws NumberFormatException, IOException {
		this.robot = robot;
		// current mouse position
		sp = MouseInfo.getPointerInfo().getLocation();
		
		myframe = new MyFrame(args[0], Integer.parseInt(args[1]));
	}
	
	// override handle to process each line
	@Override
	public void handle(String line) {
		process(line);
	}
	
	// process each log line
	private void process(String line) {
		int x = 0;
		int y = 0;
		String[] split = line.split(" ");
		op = np.getLocation(); // update old phone position
		try {
			state = split[split.length-3];
			x = Integer.parseInt(split[split.length-2]);
			y = Integer.parseInt(split[split.length-1]);
			np.setLocation(x, y); // update new phone position
		} catch (Exception e) {
			System.out.println("fail");
		}
		
		if (state.equals("DOWN2") && myframe.method.equals("two")) move(x, y);
		if (state.equals("UP2") && myframe.method.equals("one")) move(x, y);
		if (!(myframe.frame.getCursor().getType() == Cursor.DEFAULT_CURSOR)
				&& (state.equals("UP1") || state.equals("UP2"))) myframe.frame.setCursor(myframe.cursor);
		
		displacement();
	}
	
	// find displacement then move
	private void displacement() {
		if (state.equals("MOVE")) {
			sp = MouseInfo.getPointerInfo().getLocation();
			int x = sp.x + (np.x - op.x);
			int y = sp.y + (np.y - op.y);
			move(x, y);
		}
	}
	
	// move mouse
	private void move(int x, int y) {
		robot.mouseMove(x, y);
	}
}