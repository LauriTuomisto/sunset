"""This program tells the time of sunrise and sunset in a given location on a given date. For simplicity, we assume that
 the earth and the orbit are completely round"""


from math import cos, acos, tan, sqrt, pi


def datesorter(date1, date2):
    """return the given dates in chronological order, dates should be of the form (year, month, day)"""

    if date1[0] > date2[0]:
        return date2, date1
    elif date1[0] == date2[0]:
        if date1[1] > date2[1]:
            return date2, date1
        elif date1[1] == date2[1] and date1[2] > date2[2]:
            return date2, date1
    else:
        return date1, date2


def phi_validator(phi):
    """phi value is always in the range [0, 2*pi], this function can be used to check,
    and if necessary to change the value"""

    if phi < 0:
        phi = 2 * pi + phi
    if phi >= 2 * pi:
        phi = phi - 2 * pi
    return phi


def days(day1, day2):
    """Function used to calculate the amount of days between two dates.
    The arguments are of the form (year, month, day). The differences due to years, months and days are calculated
    separately and summed up in the end."""
    day1, day2 = datesorter(day1, day2)
    n_of_days = 0
    if day1[0] < day2[0]:
        if leapyear(day1[0]):
            n_of_days += 366 - months_to_days(day1[1], leap=True) - day1[2]
        else:
            n_of_days += 365 - months_to_days(day1[1]) - day1[2]
        n_of_days += months_to_days(day2[1]) + day2[2]
    else:
        n_of_days += months_to_days(day2[1]) + day2[2] - months_to_days(day1[1]) - day1[2]
    start_year = day1[0] + 1
    while start_year < day2[0]:
        if leapyear(start_year):
            n_of_days += 366
        else:
            n_of_days += 365
        start_year += 1

    return n_of_days


def months_to_days(month, leap=False):
    """Function used to calculate how many days a month corresponds to."""
    day_count = 0
    i = 1
    while i < month:
        if i in [1, 3, 5, 7, 8, 10, 12]:
            day_count += 31
        elif i in [4, 6, 9, 11]:
            day_count += 30
        elif leap:
            day_count += 29
        else:
            day_count += 28

        i += 1
    return day_count


def min_to_hour_min(min):
    """Function to convert minutes into hours and minutes."""
    hours = int(min / 60)
    mins = min % 60
    return hours, mins


def leapyear(year):
    """Function returns a boolean based on if the given value is a leapyear."""
    if year % 4 != 0:
        return False
    elif year % 100 == 0:
        if year % 400 == 0:
            return True
        else:
            return False
    else:
        return True


def geo_to_sphere(lat, long):
    """Convert geographical coordinates to sphere coordinates. Sphere coordinates are attached in a way that the point
    (0,0) in lat long coordinates is (pi/2,0) (theta, phi) in our spherical coordinate system"""
    lat_sph = pi / 2 + lat / 90 * pi / 2

    if long >= 0:
        long_sph = long / 180 * pi
    else:
        long_sph = 2 * pi + long / 180 * pi

    return lat_sph, long_sph


def day_length_helper(alpha, beta):
    """Helper function that calculates the length of a day on a given latitude depending on the sun position.
    Days increasingly shorten when moving away from the equator. Alpha angle is the angle between
        the subsolar point and the equator. Beta is the angle between the given coordinate and the North Pole."""
    if pow(cos(beta), 2) == 1:
        # to avoid division by zero
        beta -= 0.00001
    half_day = acos(tan(alpha) * cos(beta) / sqrt(1 - pow(cos(beta), 2)))
    return half_day


class Subsolar:
    """Subsolar point is the point closest to the sun.
    In our program this is essential in knowing the location of the area illuminated by the sun.
    Initially the subsolar point is at the Tropic of Cancer, and longitude is 0."""
    theta = (90 - 23.44) / 180 * pi
    phi = 0

    def earth_orbit(self, date):
        """This method simulates the movement of the subsolar point as days go by.
        For simplicity, we only check the location of the subsolar point once a day at 12.00 am UTC.
        The subsolar point moves longitudinally but since we only check the value when it is 0, we do not have to shift
        the phi coordinate of the point. When the subsolar point reaches a tropic the direction changes.
        Direction 1 means that the subsolar point is moving north and direction -1 means that the point is moving south.
        """
        n_of_days = days((2008, 12, 21), date)
        direction = 1
        hor = 0  # -pi / 182.62125
        ver = (46.88 / 180) * pi / 182.62125
        for i in range(n_of_days):
            self.phi += hor
            if self.theta + ver >= 113.44 / 180 * pi and direction == 1:
                direction = -1
                self.theta = 113.44 / 180 * pi - (self.theta + ver - 113.44 / 180 * pi)

            elif self.theta - ver <= 66.56 / 180 * pi and direction == - 1:
                self.theta = 66.56 / 180 * pi + (-(self.theta - ver) + 66.56 / 180 * pi)

                direction = 1
            elif direction == 1:

                self.theta += ver
            else:

                self.theta -= ver
            i += 1
            if self.phi <= 0:
                self.phi = 2 * pi + self.phi

    def half_day_length(self, theta2):
        """Method returns the length of a half of a day on a given latitude. Alpha angle is the angle between
        the subsolar point and the equator. Beta is the angle between the given coordinate and the North Pole.
        The helper function is derived for a situation where the given point and the subsolar point are both on
        the Northern Hemisphere. Using the fact that the length of a day is the length of the day on the opposite side
        of the earth and changing the angles allows to cover the rest of cases.
        """
        alpha = self.theta - pi / 2
        beta = pi - theta2
        if alpha >= beta or -alpha >= theta2:
            # Midnight sun
            return pi
        elif alpha >= theta2 or -alpha >= beta:
            # Polar night
            return 0
        elif self.theta <= pi / 2 <= theta2:
            # Subsolar point is on the Northern Hemisphere and the given point on the Southern.
            return day_length_helper(-alpha, beta)
        elif self.theta >= pi / 2 >= theta2:
            # Subsolar point is on the Southern Hemisphere and the given point on the Northern.
            return day_length_helper(alpha, theta2)
        elif self.theta <= pi / 2 and theta2 <= pi / 2:
            # both on the Southern
            return pi - day_length_helper(-alpha, theta2)
        else:
            # both on the Northern
            return pi - day_length_helper(alpha, beta)

    def rise_and_fall(self, theta2):
        """Method gives the phi coordinates of sunrise and sunset based on day length."""
        first = self.phi + self.half_day_length(theta2)
        second = self.phi - self.half_day_length(theta2)

        first = phi_validator(first)
        second = phi_validator(second)

        return first, second

    def one_day(self, theta2, phi2):
        """Simulates the rotation of the earth during a day minute by minute. To find out the time of sunrise and
        sunset in the given point, the phi coordinate is shifted to match the situation at the start of the 00.00 AM.
        Then we see how long does it take to cross the line from night to day and from day to night."""

        phi_at_midnight = phi2 - pi
        if phi_at_midnight < 0:
            phi_at_midnight = 2 * pi + phi_at_midnight

        first, second = self.rise_and_fall(theta2)
        minutes = []

        for i in range(1440):

            minute_ago = phi_at_midnight
            phi_at_midnight += 0.00437469
            if minute_ago < first < phi_at_midnight or 0 < first < phi_at_midnight - 2 * pi:
                minutes.append(i)
            if minute_ago < second < phi_at_midnight or 0 < second < phi_at_midnight - 2 * pi:
                minutes.append(i)
            if phi_at_midnight >= 2 * pi:
                phi_at_midnight -= 2 * pi

        if minutes[0] == minutes[1]:
            # the length of a day or night is 0 minutes
            if self.check_hemisphere(theta2):
                return 'Midnight sun'
            else:
                return 'Polar night'

        if not self.rise_or_set(theta2, minutes[0], minutes[1]):
            # we make sure that the timestamps are in the correct order
            minutes = [minutes[1], minutes[0]]

        return minutes

    def check_hemisphere(self, theta2):
        """helper method for checking the order of sunrise and sunset"""
        if pi / 2 > self.theta and pi / 2 > theta2 or pi / 2 < self.theta and pi / 2 < theta2:
            return True
        else:
            return False

    def rise_or_set(self, theta2, rise, set):
        """method for checking the order of sunrise and sunset"""
        if self.check_hemisphere(theta2):
            if set - rise > 60 * 12:
                return True
            else:
                return False
        else:
            if set - rise < 60 * 12:
                return True
            else:
                return False


if __name__ == '__main__':
    print('Hello! This program tells you the time of sunrise and sunset in a given location on a given date.\n')
    print('Give the geographical coordinates of the location you would like to know about'
          'first the latitude, then the longitude.')
    latitude = (float(input('latitude: ')))
    longitude = float(input('longitude: '))
    latitude, longitude = geo_to_sphere(latitude, longitude)
    print('Now give the date. First the day, then the month and lastly the year.\n '
          'Dates from 2008.12.21 onwards are valid.')
    day = int(input('day: '))
    month = int(input('month: '))
    year = int(input('year: '))
    date = year, month, day

    subsolar = Subsolar()
    subsolar.earth_orbit(date)
    minutes = subsolar.one_day(latitude, longitude)
    if type(minutes) == str:
        print(minutes)

    else:
        sunrise, sunset = min_to_hour_min(minutes[0]), min_to_hour_min(minutes[1])
        print(f'sun rises at {sunrise} and sets at {sunset}. The time is UTC')
