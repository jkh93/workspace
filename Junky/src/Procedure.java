import java.awt.Point;


public class Procedure {
	int[] coords = null;
	
	public Procedure(int[] coor) {
		coords = coor;
	}
	
	public Point getPoint(int i) {
		Point p = new Point(coords[i*2], coords[i*2+1]);
		return p;
	}

}
