#include <opencv2/opencv.hpp>
#include <iostream>

using namespace cv;
using namespace std;

int main()
{
	Mat img_color, img_blurred, img_gray;
	Rect rect;
	VideoCapture cap(1);

	while (1)
	{
		cap.read(img_color);

		if (img_color.empty()) {
			break;
		}

		GaussianBlur(img_color, img_blurred, Size(5, 5), 0, 0, 4);
		cvtColor(img_blurred, img_gray, COLOR_BGR2GRAY);
		threshold(img_gray, img_gray, 100, 255, THRESH_BINARY);

		vector<vector<Point>> contours; // Vector for storing contour
		vector<Vec4i> hierarchy;

		double area;
		double max_area = 0;
		int max_index = -1;
		findContours(img_gray, contours, hierarchy, CV_RETR_CCOMP, CV_CHAIN_APPROX_SIMPLE); // Find the contours in the image
		for (int i = 0; i < contours.size(); i++) {
			area = contourArea(contours[i], false);
			if (area > max_area) {
				max_area = area;
				max_index = i;
				rect = boundingRect(contours[i]);
			}
		}

		drawContours(img_color, contours, max_index, Scalar(0, 255, 0), 2, 8, hierarchy);
		rectangle(img_color, rect, Scalar(0, 0, 255), 2, 8, 0);

		imshow("Rpi", img_color);

		// ESC 키를 입력하면 종료
		if (waitKey(25) >= 0)
			break;
	}

	return 0;
}