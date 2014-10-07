import java.awt.Robot;
import java.io.File;

import org.apache.commons.io.input.Tailer;
import org.apache.commons.io.input.TailerListener;

public class Junk {
	static File file = new File("d.txt");
//	static File file = null;
	static boolean b = true;
	static Tailer tailer = null;
	
	public static void main(String args[]) throws Exception {
		// argument is $name from script
		String[] a = {"anthony", "3"};
		Robot robot = new Robot();
		TailerListener tl = new MyTailerListener(robot, a);
		tailer = new Tailer(file, tl, 10, true);
		tailer.run();
	}
	
}
